class FormatHelper{
    static DisplaySize(bytes, decimals = 2){
    if (!+bytes) return '0 Bytes'

    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

    const i = Math.floor(Math.log(bytes) / Math.log(k))

    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
    }

}
class UploadFile{
    constructor(file){
        this.size = file.size;
        this.file= file;
        this.IsUploaded = false;
        this.IsFailed = false;
        this.uploadtry = 0;
        this.IsUploadInprogress = false;
    }

    async Upload(){
        let myDropzone = null;
        // Get the element you want to check
    var element = document.getElementById("hiddenupload");

    if (element.dropzone) {
        console.log("Element has a Dropzone attached");
        myDropzone = Dropzone.forElement("#hiddenupload");
    } else {
        console.log("Element does not have a Dropzone attached");
        myDropzone = new Dropzone("#hiddenupload", { url: "/upload",  chunking: true,
        forceChunking: true,chunkSize: 1000000,maxFilesize: 5000,parallelUploads: 1});

        myDropzone.on("sending", function(file, xhr, formData) {
            formData.append("forceZip", "yes");
            formData.append("fileId", UploadHelper.Instance.file_id);
            formData.append("Path",file.webkitRelativePath);
            // Add more key-value pairs as needed
          });

        myDropzone.on("complete", function (file) {
            console.log("File upload finished:", file);
            console.log("Uploaded file of size "+FormatHelper.DisplaySize(file.size));
            UploadHelper.Instance.uploadSize += file.size;
            console.log("Uploaded Progress : "+FormatHelper.DisplaySize(UploadHelper.Instance.uploadSize)+"/"+FormatHelper.DisplaySize(UploadHelper.Instance.totalSize));
            UploadHelper.Instance.NextUpload();
          });
    }
        // Create a mock event with the File object
        var mockEvent = { dataTransfer: { files: [this.file] } };
                    
        // Trigger the drop event on the Dropzone element
        myDropzone.listeners[0].events.drop(mockEvent);
    }
}



class UploadZipFile{
    constructor(){
        this.size=0;
        this.uploadsize=0;
        //Move to Constant class
        this.allowedSize = 10485760;
        this.maxSize = 10485760;
        this.maxUploadTry = 3;
        this.fileList = [];
        this.totalChunks = 0;
        this.uploadedChunks = 0;
        this.uploadedChunkStatus = {};
        this.IsFileComplete = false;
        this.IsUploaded = false;
        this.IsFailed = false;
        this.uploadtry = 0;
        this.IsUploadInprogress = false;
    }

    AddFile(file){
        //Reject File that's bigger than 500MB -> IsComplete : false, AddFile : false
        if(file.size > this.maxSize){
            return false;
        }

        //Files greater than 10MB, add as a separate upload file -> IsComplete : true, AddFile : true
        if(this.size==0 && file.size > this.allowedSize && file.size < this.maxSize){
            this.addFileToList(file);
            this.finalizeZipFile();
            return true;
        }

        //If File to added, makes upload file cross 10MB let it be added to a new file
        //-> IsComplete : true, AddFile : false
        if(this.size + file.size > this.allowedSize){
            this.finalizeZipFile();
            return false;
        }

        //More files can be added to the current zip file. Continue adding
        //-> IsComplete : false, AddFile : true
        this.addFileToList(file);
        return true;
    }

    addFileToList(file){
        this.size = this.size + file.size;
        this.fileList.push(file);
    }

    finalizeZipFile(){
        this.IsFileComplete = true;
    }

    async Upload(){
        if(this.uploadtry > 3){
            this.IsFailed = true;
            UploadActivity.Instance.TotalUploadFailed++;
            return;
        }

        let zip = new JSZip();
        for(let i=0;i<this.fileList.length;i++){
            let file = this.fileList[i],
            name = file.webkitRelativePath || file.name;
            zip.file(name, file, {binary: true});
        }

        await zip.generateAsync({type:"blob"}).then(blob => {
          
        let myDropzone = null;
            // Get the element you want to check
        var element = document.getElementById("hiddenupload");

        if (element.dropzone) {
            console.log("Element has a Dropzone attached");
            myDropzone = Dropzone.forElement("#hiddenupload");
        } else {
            console.log("Element does not have a Dropzone attached");
            myDropzone = new Dropzone("#hiddenupload", { url: "/upload",  chunking: true,
            forceChunking: true,chunkSize: 1000000,maxFilesize:5000,parallelUploads: 1});

            myDropzone.on("complete", function (file) {
                console.log("File upload finished:", file);
                console.log("Uploaded file of size "+FormatHelper.DisplaySize(file.size));
                UploadHelper.Instance.uploadSize += file.size;
                console.log("Uploaded Progress : "+FormatHelper.DisplaySize(UploadHelper.Instance.uploadSize)+"/"+FormatHelper.DisplaySize(UploadHelper.Instance.totalSize));
                UploadHelper.Instance.NextUpload();
              });


              myDropzone.on("sending", function(file, xhr, formData) {
                formData.append("forceZip", "yes");
                formData.append("fileId", UploadHelper.Instance.file_id);
                formData.append("Path",file.webkitRelativePath);
                // Add more key-value pairs as needed
              });  
        }

            // Create a File object
            var file = new File([blob], UploadHelper.Instance.file_id +"_"+Date.now() + '.zip', { type: "application/zip" });

            // Create a mock event with the File object
            var mockEvent = { dataTransfer: { files: [file] } };
                        
            // Trigger the drop event on the Dropzone element
            myDropzone.listeners[0].events.drop(mockEvent);
        });
    }



}

class UploadHelper{
    static Instance;

    constructor(files){
        this.files = files;
        this.totalSize = 0;
        this.uploadSize = 0;
        this.splitFiles = [];
        this.Index = 0;
        this.maxWorkers = 0;
        this.InprogressUpload = 0;
        this.TotalUpload = 0;
        this.TotalUploadFailed = 0;
        this.file_id = Date.now();
    }


    // Get the files and Initialize Upload
    static InitializeUpload(files){
        this.Instance = new UploadHelper(files);
        this.Instance.SplitFilesBySize();
    }

    static InitializeFileUpload(file){
        this.Instance = new UploadHelper([file]);
        this.Instance.splitFiles.push(new UploadFile(file));
    }

    static PerformUpload(){
        this.Instance.Upload();
    }

    Upload(){
        this.Index =0;
        console.log("Triggering Index 0");
        this.splitFiles[0].Upload();
    }

    

    NextUpload(){
        this.Index = this.Index + 1;
        if(this.Index==this.splitFiles.length){
            console.log("Upload is complete");
        }else{
            this.splitFiles[this.Index].Upload();
        }
        
    }

    SplitFilesBySize(){
        console.log("SplitFilesBySize File Count: "+this.files.length);

        let uploadZipFile = new UploadZipFile();
        console.log("New Zip File created.");
        for (let i = 0; i < this.files.length; i++) {
            let file = this.files[i],
            name = file.webkitRelativePath || file.name;
            console.log("Processing File of size : "+FormatHelper.DisplaySize(file.size));
            let isFileAdded = false;
            
            while(!isFileAdded){

                isFileAdded = uploadZipFile.AddFile(file);
                console.log("Able to add file to Zip "+isFileAdded+" Current Zip File Size :"+ FormatHelper.DisplaySize(uploadZipFile.size));
                if(!isFileAdded && !uploadZipFile.IsFileComplete){
                    //Not able to handle large size file
                    //Handle separately.
                    console.log("File Size too large. Adding to separate File : "+FormatHelper.DisplaySize(file.size));
                    let uploadFile = new UploadFile(file);
                    this.splitFiles.push(uploadFile);
                    isFileAdded = true;
                    continue;
                }

                if(uploadZipFile.IsFileComplete){
                    this.splitFiles.push(uploadZipFile);
                    console.log("Zip File "+this.splitFiles.length+" is complete. Zip File size is "+FormatHelper.DisplaySize(uploadZipFile.size));
                    uploadZipFile = new UploadZipFile();
                    console.log("New Zip File created.");
                    continue;
                }
            }

            this.totalSize += file.size;

        }
        if(uploadZipFile.fileList.length>0){
            this.splitFiles.push(uploadZipFile);
            console.log("Zip File "+this.splitFiles.length+" is complete.");
        }
        console.log("SplitFilesBySize SplitFile Count: "+this.splitFiles.length);

    }

}