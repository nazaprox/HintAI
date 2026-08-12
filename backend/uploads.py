import os, uuid
from .config import ALLOWED_IMAGE_MIME_TYPES, ALLOWED_PDF_MIME_TYPES, MAX_IMAGE_SIZE_BYTES, MAX_PDF_SIZE_BYTES
UPLOAD_DIR='uploads'; os.makedirs(UPLOAD_DIR,exist_ok=True)
_FILES={}

def validate_and_save_upload(filename,mime_type,file_bytes):
    image=mime_type in ALLOWED_IMAGE_MIME_TYPES; pdf=mime_type in ALLOWED_PDF_MIME_TYPES
    if not image and not pdf:return False,{},'INVALID_FILE_TYPE'
    limit=MAX_IMAGE_SIZE_BYTES if image else MAX_PDF_SIZE_BYTES
    if len(file_bytes)>limit:return False,{},'FILE_TOO_LARGE'
    ext='.pdf' if pdf else '.jpg'
    fid='file_'+uuid.uuid4().hex
    path=os.path.join(UPLOAD_DIR,fid+ext)
    with open(path,'wb') as f:f.write(file_bytes)
    meta={'file_id':fid,'filename':filename,'mime_type':mime_type,'size':len(file_bytes),'file_path':path,'preview_url':f'/uploads/{fid}{ext}'}
    _FILES[fid]=meta
    return True,meta,''

def get_file_meta(file_id):return _FILES.get(file_id)
