from android import mActivity, autoclass, cast
from os.path import splitext,join, basename, exists
from os import mkdir

FileOutputStream = autoclass('java.io.FileOutputStream')
FileInputStream = autoclass('java.io.FileInputStream')
FileUtils        = autoclass('android.os.FileUtils')
Environment = autoclass('android.os.Environment')
MediaStoreFiles = autoclass('android.provider.MediaStore$Files')
MediaStoreAudioMedia = autoclass('android.provider.MediaStore$Audio$Media')
MediaStoreImagesMedia = autoclass('android.provider.MediaStore$Images$Media')
MediaStoreVideoMedia = autoclass('android.provider.MediaStore$Video$Media')
MediaStoreDownloads = autoclass('android.provider.MediaStore$Downloads')
MediaStoreMediaColumns = autoclass('android.provider.MediaStore$MediaColumns')
ContentValues = autoclass('android.content.ContentValues')
MimeTypeMap = autoclass('android.webkit.MimeTypeMap')
JString = autoclass('java.lang.String')
Uri = autoclass('android.net.Uri')
ContentUris = autoclass('android.content.ContentUris')

# Source https://github.com/RobertFlatt/Android-for-Python/storage

#########################
# assumes api>=29
# api=30 recomended
#########################

class SharedStorage:
    # For shared media, documents, and downloads
    ############################################
    # Shared Storage is a database, NOT a Linux file system.
    # The database is organized in Root Directories
    #  'Music'         is the Music directory
    #  'Movies'        is the Movies directory
    #  'Pictures'      is the Pictures directory
    #  'Documents'     is the Documents directory
    #  '*'             (default) one of the first 4 depending on file extension
    #  'Downloads'     is the Downloads directory
    #
    #  Within those Root Directories this app's public files are stored under
    #  its 'AppName'. Sub-directories are available.
    #
    # The database operations 'insert', 'retrieve', and 'delete' are
    # implemented. An insert overwrites an existing entry.
    #
    # Entries are defined by Root Directory, optional sub-directory, and file
    # name.
    #
    # Entries persist after this app is uninstalled.
    # 
    # The api defaults to the 'external' volume, 'internal' is available.
    #
    # No Android permissions are required to operate on this app's
    # SharedStorage.
    #
    # The api can retrive from a location in Shared Storage that is not owned by
    # this app. This requires READ_EXTERNAL_STORAGE permission.
    #
    # Two additional methods enable interoperability with the Android
    # 'android.net.Uri' class.
    #
    ###################
    #
    # Database Operations:
    # insert()      - copy a PrivateStorage file into this app's SharedStorage.
    # retrieve()    - copy a SharedStorage file to PrivateStorage, returns a
    #                 file path. 
    # delete()      - delete a file in this app's SharedStorage.
    #
    # Interoperability with Android 'android.net.Uri' class:
    # getUri()      - get a Uri from SharedStorage path,          returns Uri
    # retrieveUri() - copy SharedStorage Uri to PrivateStorage,
    #                  returns a file path
    #
    ###################
    # The API:
    #
    # insert(file_path,       
    #        root_dir = '*', 
    #        sub_dir = '',  
    #        volume = 'external') 
    #               returns True if file inserted
    #
    # retrieve(file_name           
    #        root_dir = '*'      
    #        sub_dir = '',       
    #        volume = 'external',
    #        this_app  = True)    # False requires READ_EXTERNAL_STORAGE, and
    #                             # sub_dir[0] may be another app's name. 
    #                returns a PrivateStorage file path, or a URL string
    #
    # delete(file_name,          
    #        root_dir = '*',     
    #        sub_dir = '',       
    #        volume = 'external')
    #                 returns True if file exists to delete
    #
    # getUri(file_name,          
    #        root_dir = '*',     
    #        sub_dir = '',       
    #        volume = 'external',
    #        this_app  = True)    # False requires READ_EXTERNAL_STORAGE, and
    #                             # sub_dir[0] may be another app's name. 
    #                   returns a Uri ('android.net.Uri')
    #
    # retrieveUri(uri) #A 'android.net.Uri' from some other Android Activity
    #                   returns a PrivateStorage file path.
    #     
    #######################
    #
    # Examples:
    # Where txt_file could be PrivateStorage().getFilesDir() + 'text.txt'
    # and so on.
    # All methods take a required file name, and optional directory parameters.
    #  
    #   SharedStorage().insert(txt_file, 'Documents')
    #   SharedStorage().insert(txt_file, sub_dir= 'a/b')
    #   SharedStorage().insert(txt_file, 'Downloads')
    #   SharedStorage().insert(jpg_file, 'Pictures')
    #   SharedStorage().insert(mp3_file)
    #   SharedStorage().insert(ogg_file, 'Music')
    #   path = SharedStorage().retrieve('test.txt')
    #   path = SharedStorage().retrieve('test.txt', sub_dir = 'a/b')
    #   SharedStorage().delete('test.mp3', 'Music')
    #
    #######################

    # saves a copy of a PrivateStorage file to SharedStorage, return success 
    def insert(self, file_path, root_dir = '*', sub_dir = '',
               volume = 'external'):
        success = False
        try:
            volume = volume.lower()
            if volume not in ['internal', 'external']:
                volume = 'external'
            file_name = basename(file_path)
            # delete existing
            self.delete(file_name, root_dir, sub_dir, volume)
            # build MediaStore data
            MIME_type = self._get_file_MIME_type(file_name)
            root_directory = self._get_root_directory(root_dir, MIME_type)  
            sub_directory = join(root_directory, self._app_name())
            if sub_dir:
                sub_dirs = sub_dir.split('/')
                for s in sub_dirs:
                    sub_directory = join(sub_directory,s)
            root_uri = self._get_root_uri(root_directory, volume)
            cv = ContentValues()
            cv.put(MediaStoreMediaColumns.DISPLAY_NAME, file_name)
            cv.put(MediaStoreMediaColumns.MIME_TYPE, MIME_type)  
            cv.put(MediaStoreMediaColumns.RELATIVE_PATH, sub_directory)
            # copy file
            context = mActivity.getApplicationContext()    
            uri = context.getContentResolver().insert(root_uri, cv)
            ws  = context.getContentResolver().openOutputStream(uri)
            rs = FileInputStream(file_path)
            FileUtils.copy(rs,ws)
            ws.flush()
            ws.close()
            rs.close()
            success = bool(self.getUri(file_name, root_dir, sub_dir, volume))
        except Exception as e:
            print('ERROR SharedStorage.insert():\n' + str(e))
        return success

    # delete SharedStorage entry, only for this app's entries
    def delete(self, file_name, root_dir = '*' , sub_dir = '',
               volume = 'external'):
        success = False
        try:
            fileUri = self.getUri(file_name, root_dir, sub_dir, volume)
            if fileUri:
                context = mActivity.getApplicationContext()
                context.getContentResolver().delete(fileUri,None,None)
                success = True
        except Exception as e:
            print('ERROR SharedStorage.delete():\n' + str(e))
        return success
            
    # copy SharedStorage entry to PrivateStorage cacheDir, return its file_path
    def retrieve(self, file_name, root_dir = '*', sub_dir = '', 
                 volume = 'external', this_app = True):
        uri = self.getUri(file_name, root_dir, sub_dir, volume, this_app)
        return self.retrieveUri(uri)

    # from Android 'android.net.Uri' class
    # for 'content' and 'file' uris copy the file to PrivateStorage
    # for other uris retun the uri as a string
    def retrieveUri(self, someUri):  
        new_file_path = ''
        try:
            if someUri:
                someUri = cast('android.net.Uri',someUri)
                scheme = someUri.getScheme().lower()
                if scheme == 'content':
                    context = mActivity.getApplicationContext()
                    cursor = context.getContentResolver().query(someUri, None,
                                                                None, None,
                                                                None)
                    dn = MediaStoreMediaColumns.DISPLAY_NAME
                    nameIndex = cursor.getColumnIndex(dn)
                    cursor.moveToFirst()
                    file_name = cursor.getString(nameIndex)
                    cursor.close()
                elif scheme == 'file':
                    file_name = basename(someUri.getPath())
                else:
                    #https://en.wikipedia.org/wiki/List_of_URI_schemes
                    return someUri.toString()
                # Save to
                new_file_path = PrivateStorage().getCacheDir()
                if not new_file_path:
                    new_file_path = PrivateStorage().getCacheDir('internal')
                new_file_path = join(new_file_path,"MediaStore")
                if not exists(new_file_path):
                    mkdir(new_file_path)
                new_file_path= join(new_file_path, file_name)
                # Copy
                rs = mActivity.getContentResolver().openInputStream(someUri)
                ws = FileOutputStream(new_file_path)
                FileUtils.copy(rs,ws)
                ws.flush()
                ws.close()
                rs.close()
        except Exception as e:
            print('ERROR SharedStorage.retrieveUri():\n' + str(e))
        return new_file_path
        
    # get a Java android.net.Uri 
    def getUri(self, file_name, root_dir = '*', sub_dir = '', 
               volume = 'external', this_app = True):
        fileUri = None
        try:
            volume = volume.lower()
            if volume not in ['internal', 'external']:
                volume = 'external'
            MIME_type = self._get_file_MIME_type(file_name)
            root_directory = self._get_root_directory(root_dir,MIME_type) 
            root_uri = self._get_root_uri(root_directory, volume)
            location = root_directory
            if this_app:
                location = join(location,self._app_name())
            if sub_dir:
                sub_dirs = sub_dir.split('/')
                for s in sub_dirs:
                    location = join(location,s)
            location = join(location,"")

            selection = MediaStoreMediaColumns.DISPLAY_NAME+" LIKE '"+\
                file_name+"'"
            selection += " AND "
            selection += MediaStoreMediaColumns.RELATIVE_PATH+" LIKE '"+\
                location+"'"

            context = mActivity.getApplicationContext()
            cursor = context.getContentResolver().query(root_uri,
                                                        None,
                                                        selection,
                                                        None,
                                                        None)
            while cursor.moveToNext():
                dn = MediaStoreMediaColumns.DISPLAY_NAME
                rp = MediaStoreMediaColumns.RELATIVE_PATH
                index = cursor.getColumnIndex(dn)
                fileName = cursor.getString(index)
                dindex = cursor.getColumnIndex(rp)
                dName = cursor.getString(dindex)
                if file_name == fileName:
                    id_index = cursor.getColumnIndex(MediaStoreMediaColumns._ID)
                    id = cursor.getLong(id_index)
                    fileUri = ContentUris.withAppendedId(root_uri,id)
                    break
            cursor.close()
        except Exception as e:
            print('ERROR SharedStorage.getUri():\n' + str(e))
        return fileUri

    ###########
    # utilities
    ###########

    def _get_file_MIME_type(self,file_name):
        try :
            file_ext_no_dot = ''
            file_ext = splitext(file_name)[1]
            if file_ext:
                file_ext_no_dot = file_ext[1:]
            if file_ext_no_dot:
                lower_ext  = file_ext_no_dot.lower()
                mtm = MimeTypeMap.getSingleton()
                MIME_type = mtm.getMimeTypeFromExtension(lower_ext)
                if not MIME_type:
                    MIME_type = 'application/' + file_ext_no_dot
            else:
                MIME_type = 'application/unknown' 
        except Exception as e:
            print('ERROR SharedStorage._file_MIME_type():\n' + str(e))
            MIME_type = 'application/unknown'
        return MIME_type

    def _get_root_directory(self, root_dir, MIME_type):
        if root_dir == '*':
            root, ext = MIME_type.split('/')
            if root == 'image':
                root_dir = 'pictures'
            elif root == 'video':
                root_dir = 'movies'
            elif root == 'audio':
                root_dir = 'music'
            else:
                root_dir = 'documents'
        root_dir = root_dir.lower()
        if root_dir == 'downloads':
            root_directory = Environment.DIRECTORY_DOWNLOADS
        elif root_dir == 'pictures':
            root_directory = Environment.DIRECTORY_PICTURES
        elif root_dir == 'movies':
            root_directory = Environment.DIRECTORY_MOVIES
        elif root_dir == 'music':
            root_directory = Environment.DIRECTORY_MUSIC
        else:
            root_directory = Environment.DIRECTORY_DOCUMENTS
        return root_directory

    def _get_root_uri(self, root_directory, volume):
        if root_directory == Environment.DIRECTORY_DOWNLOADS:
            root_uri = MediaStoreDownloads.getContentUri(volume)
        elif root_directory == Environment.DIRECTORY_PICTURES:
            root_uri = MediaStoreImagesMedia.getContentUri(volume)
        elif root_directory == Environment.DIRECTORY_MOVIES:
            root_uri = MediaStoreVideoMedia.getContentUri(volume)
        elif root_directory == Environment.DIRECTORY_MUSIC:
            root_uri = MediaStoreAudioMedia.getContentUri(volume)
        else:
            root_uri = MediaStoreFiles.getContentUri(volume)
        return root_uri
            
    def _app_name(self):
        context = mActivity.getApplicationContext()
        appinfo = context.getApplicationInfo()
        if appinfo.labelRes:
            name = context.getString(appinfo.labelRes)
        else:
            name = appinfo.nonLocalizedLabel.toString()
        return name


class PrivateStorage:
    # For app specific files
    # No permissions required
    # External directories that are not mounted return ''
    # FilesDir lifetime ends when app uninstalled.
    # cacheDir is temporary storage managed by Android, lifetime is undefined.
    # The install directory './' is also private storage, lifetime ends
    #   when app is updated. Use as read only of files in apk.
    # external and internal refer to the storage volume
    #
    # Examples :
    #   Install Dir:   getcwd()
    #   FilesDir:      PrivateStorage().getFilesDir()
    #   CacheDir:      PrivateStorage().getCacheDir())
    
    def getFilesDir(self , volume = 'external'):
        if volume not in ['internal', 'external']:
            volume = 'external'
        context = mActivity.getApplicationContext()
        result = ''
        if volume == 'internal':
            result = context.getFilesDir().toString()
        else:
            result =  context.getExternalFilesDir(None)
            if result:
                result = result.toString()
        return str(result)            

    def getCacheDir(self, volume = 'external'):
        if volume not in ['internal', 'external']:
            volume = 'external'
        context = mActivity.getApplicationContext()
        result = ''
        if volume == 'internal':
            result = context.getCacheDir().toString()
        else:
            result =  context.getExternalCacheDir()
            if result:
                result = result.toString()
        return str(result)

