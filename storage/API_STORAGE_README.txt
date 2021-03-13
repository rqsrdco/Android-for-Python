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
    
