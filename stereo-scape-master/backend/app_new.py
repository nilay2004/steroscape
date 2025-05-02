@app.route('/processing-status', methods=['GET'])
def get_processing_status():
    """Return the current processing status"""
    return jsonify(processing_status)

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
        return response
    
    try:
        print("Starting file upload processing...")
        global processStoped
        processStoped = False
        user_id = request.form.get('user')
        
        # Handle default user ID
        if user_id == "default_user" or not user_id:
            user_id = "default_user"
        
        settings = request.form.get('config')
        if settings:
            settings = json.loads(settings)
            
            # Override settings to use less memory
            settings['n_iterations'] = min(settings.get('n_iterations', 100), 50)  # Cap at 50 iterations
            settings['modal_depth'] = min(settings.get('modal_depth', 2), 2)       # Cap at depth 2
            settings['modal_width'] = min(settings.get('modal_width', 16), 16)     # Cap at width 16
            settings['n_samples'] = min(settings.get('n_samples', 4), 4)           # Cap at 4 samples
            
        if not len(request.files):
            return jsonify({'success': 0, 'error': "emptyRequest", 'message': "Please add some images of the object from different view points"})
        
        print(f"Received {len(request.files)} files for processing")
        
        fn = randomString(10)
        p = os.getcwd()+'/media/' + fn 
        os.mkdir(p) 
        files = []
        i = 0
        isVideo = False
        isNPZ = False 
        
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
            return jsonify({'message': 'Failed please select more 4 images.', 'success': 0})

        # FORCE very small images for the resizing regardless of settings
        # This ensures the NeRF process won't run out of memory
        size = (16, 16)  # Extremely small size to prevent OOM errors
        
        npzDatasetPath = ''

        if isNPZ == False:
            print("Processing image or video files...")
            if isVideo:
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
                print(f"Processed {numberOfImages} images")

            print("Setting up dataset...")
            # Force garbage collection before dataset creation
            gc.collect()
            
            ds = setupDataset(p, False, emit=None)
            if ds.isDatasetCreated():
                npzDatasetPath = ds.output_npz
                print(f"Dataset created at {npzDatasetPath}")
            else:
                print("Failed to create dataset")
        else:
            npzDatasetPath = files[0]
            print(f"Using provided NPZ dataset: {npzDatasetPath}")

        if npzDatasetPath != '':
            print("Starting NeRF processing...")
            # Force garbage collection before NeRF processing
            gc.collect()
            
            # Create a limited NeRF model with reduced parameters
            nerf = NeRF(
                emit=None, 
                checkProcessExecution=checkProcessExecution, 
                config=settings, 
                media_path=p, 
                save_modal=True
            )
            nerf.loadDataset(npzDatasetPath)
            
            # Run with try/except to catch memory errors
            try:
                nerf.Run()
                print("NeRF processing completed")
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
                nerf = NeRF(
                    emit=None, 
                    checkProcessExecution=checkProcessExecution, 
                    config=minimal_settings, 
                    media_path=p, 
                    save_modal=True
                )
                nerf.loadDataset(npzDatasetPath)
                try:
                    nerf.Run()
                    print("NeRF processing completed with minimal settings")
                except Exception as e2:
                    print(f"Failed even with minimal settings: {e2}")
                    return jsonify({'message': f"System doesn't have enough memory for NeRF processing: {str(e2)}", 'success': 0})
        else:
            print("Dataset creation failed")
            return jsonify({'message': "Creating dataset failed. Please try again later.", 'success': 0})
            
        if processStoped:
            print("Process was stopped by user")
            deleteFilesAndFolder(p, deleteFolder=True, deleteFiles=True)
            return jsonify({'message': "Processing Stopped!", 'success': 0})
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
            return jsonify({'message': 'Complete!', 'success': 1, 'media': fn})
    except Exception as e:
        print(f"Error processing files: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f"Error processing files: {str(e)}", 'success': 0})

# Other routes will be minimally implemented for testing

if __name__ == "__main__":
    print(f"Running Flask on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 