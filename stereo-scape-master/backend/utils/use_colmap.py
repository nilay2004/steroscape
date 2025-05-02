import random
import subprocess
import os
import shutil
# from .fun__ import deleteFilesAndFolder

class COLMAP:
    def __init__(self, images_path, emit, checkProcessExecution):
        self.images_path = images_path
        self.project_path = f"{os.getenv('colmap')}\\outputs\\"
        self.sparse = f"{os.getenv('colmap')}\\outputs\\sparse\\"
        self.colmap = f"{os.getenv('colmap')}\\COLMAP.bat"
        self.output_txt = f"{os.getenv('colmap')}\\"
        self.emit = emit
        self.total_functions = 5
        self.error = False
        self.checkProcessExecution = checkProcessExecution
        self.startProcess()

    def startProcess(self) :
        pipe = [
            self.ExtractFeatures, 
            self.ConvertModel, 
            self.delete_colmap_outputs]
        for _ in pipe:
            if self.checkProcessExecution():
                return None
            else:
                _()

    def ExtractFeatures(self):
        # command = f'{self.colmap} feature_extractor  --database_path {self.db_path} --image_path {self.images_path} --num_threads 4 --max_num_features 2000 --feature_type sift --sift_num_octaves 5 --sift_octave_resolution 1.6'
        # command = f"{self.colmap} automatic_reconstructor --project_path {self.project_path}"
        self.emit('progress', {'process': 'colmap', 'title': 'Extracting Features from images', 'progress': random.randint(0, 90)})
        command = f'{self.colmap} automatic_reconstructor --workspace_path {self.project_path} --image_path {self.images_path} --data_type individual --quality normal'
        subprocess.run(['cmd', '/c', 
            command
        ])
        self.emit('progress', {'process': 'colmap', 'title': 'Extracting Features from images', 'progress': 68})
        print('feature extracting done')

    def ExhaustiveMatcher(self):
        command = f'{self.colmap} exhaustive_matcher --database_path {self.db_path}'
        # command = f'{self.colmap} exhaustive_matcher --project_path {self.project_path}'
        # command
        subprocess.run(['cmd', '/c', command])
        self.emit('progress', {'process': 'colmap', 'title': 'Colmap exhaustive matcher', 'progress': 2 / self.total_functions * 100})
        print('Mathcher done')
    
    def Mapper(self):
        command = f'{self.colmap} mapper --database_path {self.db_path} --image_path {self.images_path} --output_path {self.sparse}'
        # command = f'{self.colmap} mapper --project_path {self.project_path}'
        subprocess.run(['cmd', '/c', command]) 
        self.emit('progress', {'process': 'colmap', 'title': 'Colmap mapper', 'progress': 3 / self.total_functions * 100})
        print('Mapper done!')

    def ConvertModel(self):
        if os.path.exists(self.sparse+'0/'):
            if not os.path.exists(self.sparse + '0/images.bin'):
                self.error = True
                self.emit('progress', {'message': 'Colmap is failed to extract features from image. but we can move forward with default data.', 'process': 'colmap', 'title': 'Extracting features failed ❌', 'progress': 4 / self.total_functions * 100})
                return 0
            subprocess.run(['cmd', '/c', 
            f'{self.colmap} model_converter --input_path {self.sparse}0/ --output_path {self.output_txt} --output_type TXT']) 
            self.emit('progress', {'process': 'colmap', 'title': 'Converting colmap models', 'progress': 4 / self.total_functions * 100})
            print('Converting model done')

        else:
            print("=> sparse folder not exist")
            self.error = True
            self.emit('progress', {'message': 'Colmap is failed to extract features from image. but we can move forward with default data.', 'process': 'colmap', 'title': 'Extracting features failed ❌', 'progress': 4 / self.total_functions * 100})

    

    def delete_colmap_outputs(self):
        shutil.rmtree(self.project_path)
        os.mkdir(self.project_path)
        if not self.error:
            self.emit('progress', {'process': 'colmap', 'title': 'Clearing up files', 'progress': 5 / self.total_functions * 100})

# if __name__ == '__main__':
#     os.environ['colmap'] = f'{os.getcwd()}\\colmap\\'
#     def checkProcessExecution():
#         return 
#     def emit(a, b):
#         print(a, b)
    
#     COLMAP('F:\\final_year\\backend\\colmap\\project\\images\\', emit, checkProcessExecution)