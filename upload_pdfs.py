from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

auth = GoogleAuth()
auth.LocalWebserverAuth()
drive = GoogleDrive(auth)

for file in drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList():
    if file['title'] == 'university':
        file.Delete()

# Create the basedir for the PDFs
basedir = drive.CreateFile({
    'title': 'university',
    'mimeType': 'application/vnd.google-apps.folder'
})
basedir.Upload()

ids = {'src': basedir['id']}

for root, directories, files in os.walk('src', topdown=True):
    parent = ids[root.split(os.sep)[-1]]
    # Create the initial empty folder structure
    for directory in directories:
        folder = drive.CreateFile({
            'title': directory,
            'parents': [{'kind': 'drive#parentReference', 'id': parent}],
            'mimeType': 'application/vnd.google-apps.folder'
        })
        folder.Upload()
        ids[directory] = folder['id']
    # Compile the TeX files and upload the generated PDFs to the corresponding folders
    for file in files:
        if file.endswith('.tex'):
            pdf = drive.CreateFile({
                'title': file.split('.')[0],
                'parents': [{'kind': 'drive#parentReference', 'id': parent}],
                'mimeType': 'application/pdf'
            })
            compile_command = 'pdflatex -interaction nonstopmode -output-directory ' + root.replace(os.sep, '/') + ' ' + os.path.join(root, file).replace(os.sep, '/')
            os.system(compile_command)
            os.system(compile_command)
            pdf.SetContentFile(os.path.join(root, file.split('.')[0] + '.pdf'))
            pdf.Upload()

# Clean up the src directory after the compilation of all the TeX files
for root, directories, files in os.walk('src'):
    for file in files:
        if file.endswith(('.aux', '.log', '.pdf', '.synctex.gz', '.thm')):
            os.remove(os.path.join(root, file))
