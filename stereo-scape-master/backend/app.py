import json
from math import e
from time import process_time
from turtle import isvisible
from bson import ObjectId
from flask import Flask, request, send_from_directory, make_response, jsonify
import os
import platform
import sys
from flask_cors import CORS
from utils.load_model import LoadNeRF
from utils.fun__ import deleteFilesAndFolder, randomString, resizeAndSave, saveAndExtractPoses
from utils.setup_dataset import setupDataset
from db_ops.ops import saveUsersData, updateVideoPath
from utils.use_colmap import COLMAP
from utils.nerf import NeRF
import gc
import tensorflow as tf

# Create necessary directories
def ensure_directories():
    dirs_to_create = ['media', 'videos', 'results', 'colmap']
    for d in dirs_to_create:
        dir_path = os.path.join(os.getcwd(), d)
        if not os.path.exists(dir_path):
            print(f"Creating directory: {dir_path}")
            os.makedirs(dir_path)

# Ensure directories exist
ensure_directories()

# Setup environment variables and determine OS
is_windows = platform.system() == "Windows"
os.environ['colmap'] = f'{os.getcwd()}\\colmap\\'

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB max upload
app.config['MAX_FORM_MEMORY_SIZE'] = 1024 * 1024 * 1024  # 1GB for form data
app.config['MAX_FORM_CONTENT_PIECES'] = 100000  # Increase maximum number of form parts

# Increase timeouts
app.config['FLASK_RUN_THREADED'] = True
app.config['REQUEST_TIMEOUT'] = 900  # 15 minutes timeout

# Setup simple CORS
CORS(app)

# Global variables to track processing status
processing_status = {
    "status": "idle",  # idle, processing, complete, failed
    "percentage": 0,
    "message": ""
}

processStoped = False

@app.route('/')
def index():
    return {'message': 'StereoScape API is running. Use the frontend application to interact with the API.', 'status': 'ok'}

@app.route('/ping')
def ping():
    """Simple ping endpoint to test if the server is running"""
    return jsonify({'status': 'ok', 'message': 'pong'})

@app.route('/results/<path:filename>')
def sendResultImage(filename):
    return send_from_directory('results', filename)

@app.route('/videos/<path:filename>')
def sendFiles(filename):
    return send_from_directory('videos', filename)

@app.route('/media/<path:filename>')
def sendMedia(filename):
    return send_from_directory('media', filename)

@app.route('/stop-process', methods=['POST'])
def handle_stop():
    global processStoped
    processStoped = True
    return jsonify({'success': True})

def checkProcessExecution(message=''):
    global processStoped
    if processStoped:
        return True
    return False

@app.route('/get-visualz', methods=['GET'])
def getVisualz():
    try:
        theta = request.args.get('theta')
        phi = request.args.get('phi')
        rad = request.args.get('radius')
        prevImg = request.args.get('prevImg')
        if not theta:
            theta = 0
        if not phi:
            phi = 0
        if not rad:
            rad = 0
        media = request.args.get('media')
        
        # Check if media exists
        media_path = os.path.join(os.getcwd(), 'media', media)
        if not os.path.exists(media_path):
            return jsonify({
                'status': 'error',
                'message': f'Media "{media}" not found. Please upload images first.',
                'error': 'media_not_found'
            }), 404
            
        # Check if model exists
        model_path = os.path.join(media_path, 'saved_model')
        if not os.path.exists(model_path):
            return jsonify({
                'status': 'error',
                'message': f'Model for media "{media}" not found. Please process the images first.',
                'error': 'model_not_found'
            }), 404
            
        model = LoadNeRF(media)
        img = model.getView(int(theta), float(phi), float(rad), str(prevImg))
        return img
    except Exception as e:
        print("Error in getVisualz:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': 'Error processing visualization request.',
            'error': str(e)
        }), 500

@app.route('/generate-video', methods=["POST"])
def generateVideo():
    form = request.form
    media = form.get('media')
    user = form.get('user')
    _id = form.get('_id')
    model = LoadNeRF(media)
    outupt = model.Video360()
    updateVideoPath(_id, outupt)
    return jsonify({'message': 'Successfully generated!', 'success': 1, 'video': outupt})

@app.route('/load-project/<string:media>/get-view', methods=['GET'])
def LoadModel(media):
    model = LoadNeRF(media)
    img_path = model.getView()
    outupt = model.Video360()
    return jsonify({'message': 'success', 'image_path': img_path, 'success': 1, 'video': outupt})

@app.route('/files', methods=['OPTIONS'])
def files_options():
    """Handle preflight OPTIONS requests for the files endpoint"""
    response = make_response()
    return response

@app.route('/files', methods=['POST'])
def Files():
    """Handle file uploads for NeRF processing"""
    # Add CORS headers for this specific route
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    try:
        # Create response with CORS headers to allow frontend access
        def create_cors_response(response_data):
            response = jsonify(response_data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return response
            
        print("Starting file upload processing...")
        global processStoped
        global processing_status
        processStoped = False
        
        # Update processing status at the start
        processing_status = {
            "status": "processing",
            "percentage": 0,
            "message": "Starting upload processing"
        }
        
        user_id = request.form.get('user')
        
        # Handle default user ID
        if user_id == "default_user" or not user_id:
            user_id = "default_user"
        
        settings = request.form.get('config')
        if settings:
            try:
                settings = json.loads(settings)
                
                # Override settings to use less memory
                settings['n_iterations'] = min(settings.get('n_iterations', 100), 20)  # Cap at 20 iterations
                settings['modal_depth'] = min(settings.get('modal_depth', 2), 1)       # Cap at depth 1
                settings['modal_width'] = min(settings.get('modal_width', 16), 8)     # Cap at width 8
                settings['n_samples'] = min(settings.get('n_samples', 4), 2)           # Cap at 2 samples
            except Exception as e:
                print(f"Error parsing settings JSON: {str(e)}")
                processing_status = {
                    "status": "failed",
                    "percentage": 0,
                    "message": f"Error in settings: {str(e)}"
                }
                return create_cors_response({'success': 0, 'error': "settings_error", 'message': f"Error in settings: {str(e)}"})
        
        if not len(request.files):
            processing_status = {
                "status": "failed",
                "percentage": 0,
                "message": "No files uploaded"
            }
            return create_cors_response({'success': 0, 'error': "emptyRequest", 'message': "Please add some images of the object from different view points"})
        
        print(f"Received {len(request.files)} files for processing")
        processing_status["message"] = f"Processing {len(request.files)} files"
        
        fn = randomString(10)
        p = os.getcwd()+'/media/' + fn 
        os.mkdir(p) 
        files = []
        i = 0
        isVideo = False
        isNPZ = False 
        
        print("Processing uploaded files...")
        processing_status["percentage"] = 10
        for f in request.files:
            i = i + 1
            file = request.files[f]
            ex = file.filename.split('.')[-1]
            fp = p + '/'
            if ex == 'mp4': 
                isVideo = True
                fp = fp + 'vid-'
            
            if ex == 'npz':
                isNPZ = True
                fp = fp + 'dataset.npz'
                file.save(fp)
                files.append(fp)
            else:
                fp = fp + str(i) + '.' + ex
                files.append([file, fp])
                
        print(f"Processed {i} files. isVideo={isVideo}, isNPZ={isNPZ}")
        processing_status["percentage"] = 20
        processing_status["message"] = "Files uploaded, preparing processing"

        if (isVideo == False and isNPZ == False) and len(files) < 4:
            processStoped = True
            processing_status = {
                "status": "failed",
                "percentage": 0,
                "message": "Not enough images (minimum 4)"
            }
            return create_cors_response({'message': 'Failed please select more 4 images.', 'success': 0})

        # Update the size setting to be more reasonable but still memory efficient
        size = (128, 128)  # Small but not tiny images 
        
        npzDatasetPath = ''
        processing_status["percentage"] = 30
        processing_status["message"] = "Processing images"

        if isNPZ == False:
            print("Processing image or video files...")
            if isVideo:
                print("Extracting frames from video...")
                processing_status["message"] = "Extracting frames from video"
                _, fsize, numberOfImages = saveAndExtractPoses(files[0], outputFolder=p, size=size, emit=None)
                print(f"Extracted {numberOfImages} frames from video")
            else:
                numberOfImages = 0
                fsize = 0
                print("Processing individual images...")
                processing_status["message"] = "Processing individual images"
                for file in files:
                    _, fz = resizeAndSave(file[0], file[1], size)
                    if type(fsize) == int:
                        fsize += fz
                    numberOfImages += 1
                print(f"Processed {numberOfImages} images")

            print("Setting up dataset...")
            processing_status["percentage"] = 40
            processing_status["message"] = "Creating dataset"
            # Force garbage collection before dataset creation
            gc.collect()
            
            print("Setting up dataset...")
            try:
                ds = setupDataset(p, False, emit=None)
                if ds.isDatasetCreated():
                    npzDatasetPath = ds.output_npz
                    processing_status["percentage"] = 50
                    processing_status["message"] = "Dataset created, starting NeRF processing"
                    print(f"Dataset created at {npzDatasetPath}")
                else:
                    print("Failed to create dataset")
                    processing_status = {
                        "status": "failed",
                        "percentage": 0,
                        "message": "Failed to create dataset from images"
                    }
                    return create_cors_response({'message': 'Failed to create dataset. Please try different images.', 'success': 0})
            except Exception as e:
                print(f"Error creating dataset: {str(e)}")
                import traceback
                traceback.print_exc()
                processing_status = {
                    "status": "failed",
                    "percentage": 0,
                    "message": f"Error creating dataset: {str(e)}"
                }
                return create_cors_response({'message': f'Error creating dataset: {str(e)}', 'success': 0})
        else:
            npzDatasetPath = files[0]
            print(f"Using provided NPZ dataset: {npzDatasetPath}")
            processing_status["message"] = "Using provided dataset"

        def update_nerf_progress(percent_or_data, message=None, psnr=None):
            # Handle both formats of emit calls
            if isinstance(percent_or_data, str) and percent_or_data == 'progress':
                # Format: emit('progress', {...})
                data = message
                if 'training' in data and 'psnr' in data['training']:
                    processing_status["psnr"] = data['training']['psnr']
                processing_status["percentage"] = data.get('progress', 0)
                processing_status["message"] = data.get('title', '')
            else:
                # Format: emit(percent, message, psnr)
                scaled_percent = 50 + (percent_or_data * 0.4)
                processing_status["percentage"] = min(int(scaled_percent), 99)
                processing_status["message"] = message
                if psnr is not None:
                    processing_status["psnr"] = psnr

        if npzDatasetPath != '':
            print("Starting NeRF processing...")
            # Force garbage collection before NeRF processing
            gc.collect()
            
            # Create a NeRF model with more reasonable parameters
            try:
                nerf = NeRF(
                    emit=update_nerf_progress,  # Pass the progress update function
                    checkProcessExecution=checkProcessExecution, 
                    config=settings, 
                    media_path=p, 
                    save_modal=True
                )
                nerf.loadDataset(npzDatasetPath)
            except Exception as e:
                print(f"Error creating or loading NeRF model: {str(e)}")
                import traceback
                traceback.print_exc()
                processing_status = {
                    "status": "failed",
                    "percentage": 0,
                    "message": f"Error initializing NeRF: {str(e)}"
                }
                return create_cors_response({'message': f'Error initializing NeRF: {str(e)}', 'success': 0})
            
            # Run with try/except to catch memory errors
            try:
                nerf.Run()
                print("NeRF processing completed")
                processing_status["percentage"] = 95
                processing_status["message"] = "NeRF processing completed"
            except (tf.errors.ResourceExhaustedError, MemoryError) as e:
                print(f"Memory error during NeRF processing: {e}")
                # Try again with even lower settings
                del nerf
                gc.collect()
                
                minimal_settings = {
                    'n_iterations': 20,
                    'modal_depth': 1,
                    'modal_width': 8,
                    'n_samples': 2
                }
                
                print("Retrying with minimal settings...")
                processing_status["message"] = "Retrying with minimal settings"
                
                try:
                    nerf = NeRF(
                        emit=update_nerf_progress,
                        checkProcessExecution=checkProcessExecution, 
                        config=minimal_settings, 
                        media_path=p, 
                        save_modal=True
                    )
                    nerf.loadDataset(npzDatasetPath)
                    nerf.Run()
                    print("NeRF processing completed with minimal settings")
                    processing_status["percentage"] = 95
                    processing_status["message"] = "NeRF processing completed with minimal settings"
                except Exception as e2:
                    print(f"Error during retry with minimal settings: {str(e2)}")
                    import traceback
                    traceback.print_exc()
                    processing_status = {
                        "status": "failed",
                        "percentage": 0,
                        "message": f"Error during processing with minimal settings: {str(e2)}"
                    }
                    return create_cors_response({'message': f"Error during processing: {str(e2)}", 'success': 0})
        else:
            print("Dataset creation failed")
            processing_status = {
                "status": "failed",
                "percentage": 0,
                "message": "Creating dataset failed"
            }
            return create_cors_response({'message': "Creating dataset failed. Please try again later.", 'success': 0})
            
        if processStoped:
            print("Process was stopped by user")
            deleteFilesAndFolder(p, deleteFolder=True, deleteFiles=True)
            processing_status = {
                "status": "failed",
                "percentage": 0,
                "message": "Processing stopped by user"
            }
            return create_cors_response({'message': "Processing Stopped!", 'success': 0})
        else:
            print("Processing completed successfully")
            processing_status = {
                "status": "complete",
                "percentage": 100,
                "message": "Processing complete"
            }
            col_d = {
                'user': user_id if user_id == "default_user" else ObjectId(user_id), 
                'images_len': numberOfImages, 
                'psnrs': nerf.psnrs, 
                'media': fn, 
                'size': {'images': fsize}
            }
            saveUsersData(col_d)
            return create_cors_response({'message': 'Complete!', 'success': 1, 'media': fn, 'psnrs': nerf.psnrs})
    except Exception as e:
        print(f"Error processing files: {str(e)}")
        import traceback
        traceback.print_exc()
        processing_status = {
            "status": "failed",
            "percentage": 0,
            "message": f"Error: {str(e)}"
        }
        return create_cors_response({'message': f"Error processing files: {str(e)}", 'success': 0})

@app.route('/processing-status', methods=['GET'])
def get_processing_status():
    """Return the current processing status"""
    response = jsonify(processing_status)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads with processing status tracking"""
    global processing_status
    global processStoped
    
    # Reset processing status at the start of new upload
    processing_status = {
        "status": "processing",
        "percentage": 0,
        "message": "Starting upload"
    }
    
    try:
        print("Starting file upload processing...")
        processStoped = False
        user_id = request.form.get('user')
        
        # Handle default user ID
        if user_id == "default_user" or not user_id:
            user_id = "default_user"
        
        settings = request.form.get('config')
        if settings:
            settings = json.loads(settings)
            
            # Override settings to use less memory
            settings['n_iterations'] = min(settings.get('n_iterations', 100), 20)  # Cap at 20 iterations
            settings['modal_depth'] = min(settings.get('modal_depth', 2), 1)       # Cap at depth 1
            settings['modal_width'] = min(settings.get('modal_width', 16), 8)     # Cap at width 8
            settings['n_samples'] = min(settings.get('n_samples', 4), 2)           # Cap at 2 samples
        
        if not len(request.files):
            processing_status["status"] = "failed"
            processing_status["message"] = "No files uploaded"
            return create_cors_response({'success': 0, 'error': "emptyRequest", 'message': "Please add some images of the object from different view points"})
        
        processing_status["percentage"] = 10
        processing_status["message"] = "Files received, starting processing"
        
        print(f"Received {len(request.files)} files for processing")
        
        fn = randomString(10)
        p = os.getcwd()+'/media/' + fn 
        os.mkdir(p) 
        files = []
        i = 0
        isVideo = False
        isNPZ = False 
        
        processing_status["percentage"] = 20
        processing_status["message"] = "Storing uploaded files"
        
        print("Processing uploaded files...")
        for f in request.files:
            i = i + 1
            file = request.files[f]
            ex = file.filename.split('.')[-1]
            fp = p + '/'
            if ex == 'mp4': 
                isVideo = True
                fp = fp + 'vid-'
            
            if ex == 'npz':
                isNPZ = True
                fp = fp + 'dataset.npz'
                file.save(fp)
                files.append(fp)
            else:
                fp = fp + str(i) + '.' + ex
                files.append([file, fp])
                
        print(f"Processed {i} files. isVideo={isVideo}, isNPZ={isNPZ}")

        if (isVideo == False and isNPZ == False) and len(files) < 4:
            processStoped = True
            processing_status["status"] = "failed"
            processing_status["message"] = "Not enough images (minimum 4 required)"
            return create_cors_response({'message': 'Failed please select more 4 images.', 'success': 0})

        processing_status["percentage"] = 30
        processing_status["message"] = "Processing images"
        
        # FORCE very small images for the resizing regardless of settings
        # This ensures the NeRF process won't run out of memory
        size = (16, 16)  # Extremely small size to prevent OOM errors
        
        npzDatasetPath = ''

        if isNPZ == False:
            print("Processing image or video files...")
            if isVideo:
                processing_status["message"] = "Extracting frames from video"
                print("Extracting frames from video...")
                _, fsize, numberOfImages = saveAndExtractPoses(files[0], outputFolder=p, size=size, emit=None)
                print(f"Extracted {numberOfImages} frames from video")
            else:
                numberOfImages = 0
                fsize = 0
                print("Processing individual images...")
                for file in files:
                    _, fz = resizeAndSave(file[0], file[1], size)
                    if type(fsize) == int:
                        fsize += fz
                    numberOfImages += 1
                    # Update progress periodically
                    if numberOfImages % 5 == 0:
                        processing_status["percentage"] = min(30 + (numberOfImages // 5), 40)
                        processing_status["message"] = f"Processed {numberOfImages} images"
                print(f"Processed {numberOfImages} images")

            processing_status["percentage"] = 40
            processing_status["message"] = "Setting up dataset"
            
            # Force garbage collection before dataset creation
            gc.collect()
            
            print("Setting up dataset...")
            try:
                ds = setupDataset(p, False, emit=None)
                if ds.isDatasetCreated():
                    npzDatasetPath = ds.output_npz
                    processing_status["percentage"] = 50
                    processing_status["message"] = "Dataset created, starting NeRF processing"
                    print(f"Dataset created at {npzDatasetPath}")
                else:
                    print("Failed to create dataset")
                    processing_status = {
                        "status": "failed",
                        "percentage": 0,
                        "message": "Failed to create dataset from images"
                    }
                    return create_cors_response({'message': 'Failed to create dataset. Please try different images.', 'success': 0})
            except Exception as e:
                print(f"Error creating dataset: {str(e)}")
                import traceback
                traceback.print_exc()
                processing_status = {
                    "status": "failed",
                    "percentage": 0,
                    "message": f"Error creating dataset: {str(e)}"
                }
                return create_cors_response({'message': f'Error creating dataset: {str(e)}', 'success': 0})
        else:
            npzDatasetPath = files[0]
            processing_status["percentage"] = 50
            processing_status["message"] = "Using provided dataset, starting NeRF processing"
            print(f"Using provided NPZ dataset: {npzDatasetPath}")

        if npzDatasetPath != '':
            print("Starting NeRF processing...")
            
            # Force garbage collection before NeRF processing
            gc.collect()
            
            # Custom progress update function for NeRF processing
            def update_nerf_progress(percent_or_data, message=None, psnr=None):
                # Handle both formats of emit calls
                if isinstance(percent_or_data, str) and percent_or_data == 'progress':
                    # Format: emit('progress', {...})
                    data = message
                    if 'training' in data and 'psnr' in data['training']:
                        processing_status["psnr"] = data['training']['psnr']
                    processing_status["percentage"] = data.get('progress', 0)
                    processing_status["message"] = data.get('title', '')
                else:
                    # Format: emit(percent, message, psnr)
                    scaled_percent = 50 + (percent_or_data * 0.4)
                    processing_status["percentage"] = min(int(scaled_percent), 99)
                    processing_status["message"] = message
                    if psnr is not None:
                        processing_status["psnr"] = psnr
            
            # Create NeRF model with memory-efficient settings
            try:
                nerf = NeRF(
                    emit=update_nerf_progress, 
                    checkProcessExecution=checkProcessExecution, 
                    config=settings, 
                    media_path=p, 
                    save_modal=True
                )
                nerf.loadDataset(npzDatasetPath)
                nerf.Run()
                
                processing_status["percentage"] = 90
                processing_status["message"] = "NeRF processing completed, finalizing"
                print("NeRF processing completed")
            except (tf.errors.ResourceExhaustedError, MemoryError) as e:
                print(f"Memory error during NeRF processing: {e}")
                processing_status["percentage"] = 60
                processing_status["message"] = "Retrying with minimal settings due to memory constraints"
                
                # Clean up and try again with even lower settings
                del nerf
                gc.collect()
                
                minimal_settings = {
                    'n_iterations': 20,
                    'modal_depth': 1,
                    'modal_width': 8,
                    'n_samples': 2
                }
                
                print("Retrying with minimal settings...")
                try:
                    nerf = NeRF(
                        emit=update_nerf_progress, 
                        checkProcessExecution=checkProcessExecution, 
                        config=minimal_settings, 
                        media_path=p, 
                        save_modal=True
                    )
                    nerf.loadDataset(npzDatasetPath)
                    nerf.Run()
                    processing_status["percentage"] = 90
                    processing_status["message"] = "NeRF processing completed with minimal settings, finalizing"
                    print("NeRF processing completed with minimal settings")
                except Exception as e2:
                    print(f"Failed even with minimal settings: {e2}")
                    processing_status["status"] = "failed"
                    processing_status["message"] = f"System doesn't have enough memory for NeRF processing"
                    return create_cors_response({'message': f"System doesn't have enough memory for NeRF processing", 'success': 0})
        else:
            processing_status["status"] = "failed"
            processing_status["message"] = "Dataset creation failed"
            print("Dataset creation failed")
            return create_cors_response({'message': "Creating dataset failed. Please try again later.", 'success': 0})
            
        if processStoped:
            processing_status["status"] = "failed"
            processing_status["message"] = "Process stopped by user"
            print("Process was stopped by user")
            deleteFilesAndFolder(p, deleteFolder=True, deleteFiles=True)
            return create_cors_response({'message': "Processing Stopped!", 'success': 0})
        else:
            print("Processing completed successfully")
            col_d = {
                'user': user_id if user_id == "default_user" else ObjectId(user_id), 
                'images_len': numberOfImages, 
                'psnrs': nerf.psnrs, 
                'media': fn, 
                'size': {'images': fsize}
            }
            saveUsersData(col_d)
            
            # Set final status
            processing_status["status"] = "complete"
            processing_status["percentage"] = 100
            processing_status["message"] = "Processing complete"
            
            return create_cors_response({'message': 'Complete!', 'success': 1, 'media': fn})
    except Exception as e:
        # Update status on failure
        processing_status["status"] = "failed"
        processing_status["percentage"] = 0
        processing_status["message"] = f"Error: {str(e)}"
        
        print(f"Error processing files: {str(e)}")
        import traceback
        traceback.print_exc()
        return create_cors_response({'message': f"Error processing files: {str(e)}", 'success': 0})

if __name__ == "__main__":
    print(f"Running Flask on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 