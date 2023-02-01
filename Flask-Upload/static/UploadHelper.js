
class UploadZipFile{
    constructor(){
        this.size=0;
        //Move to Constant class
        this.allowedSize = 10485760;
        this.maxSize = 504857600;
        this.maxUploadTry = 3;
        this.fileList = [];
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
            let ajax = new XMLHttpRequest(),
            formData = new FormData();
            // Add the blob to the data to be sent to the server
            formData.append('zipFile', blob, UploadActivity.Instance.file_id +"_"+Date.now() + '.zip');
           
           
            ajax.addEventListener('load', function(e) {
                this.IsUploadInprogress = false;
                UploadActivity.Instance.InprogressUpload--;

                if (ajax.readyState === 4 && ajax.status === 200) {
                    UploadActivity.Instance.uploadSize += Number(ajax.getResponseHeader("filesize"));
                
                    statusElement.innerText = "Uploaded  "+formatBytes(UploadActivity.Instance.uploadSize) +" of "+formatBytes(UploadActivity.Instance.totalSize);
                    this.IsUploaded = true;
                    UploadActivity.Instance.TotalUpload++;
                    console.log("Upload Completed");
                    UploadActivity.Instance.NextUpload();
                }else{
                    this.uploadtry = this.uploadtry + 1;
                }
                
            }, false);
            
            ajax.open('POST', 'http://127.0.0.1:5000/upload', true);
            ajax.setRequestHeader("filesize",this.size);
            // We can't actually upload from here, so just download it instead
            this.IsUploadInprogress = true;
            UploadActivity.Instance.InprogressUpload++;
            ajax.send(formData);

        });
    }

}

class UploadActivity{
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

    static InitializeUpload(files){
        this.Instance = new UploadActivity(files);
        this.Instance.SplitFilesBySize();
    }

    static PerformUpload(numWorkers){
        this.Instance.Upload(numWorkers);
    }

    Upload(numWorkers){
        this.maxWorkers = numWorkers;
        console.log("Triggering Index 0");
        this.splitFiles[0].Upload();
    }

    TriggerPendingIfAny(nextTriggerCount){
        let pendingIndex = []
        for(let i=0;i<this.splitFiles.length;i++){
            let file = this.splitFiles[i];
            if(!file.IsUploaded && !file.IsFailed){
                pendingIndex.push(i);
            }
        }

        for(let j=0; j<pendingIndex.length && j<nextTriggerCount;j++){
            //this.splitFiles[j].Upload();
        }
    }

    NextUpload(){
        let nextTriggerCount = this.maxWorkers - this.InprogressUpload;
        console.log("InProgress : "+this.InprogressUpload+" Next Trigger Count : "+nextTriggerCount+ " Index : "+this.Index +" splitfiles length "+this.splitFiles.length);
        
        if(this.Index>=this.splitFiles.length-1)
        {
            if(this.TotalUpload!=this.splitFiles.length){
                this.TriggerPendingIfAny(nextTriggerCount);
            }else{
                //Say we are done

                console.log("Upload has completed : Uploaded  "+formatBytes(UploadActivity.Instance.uploadSize) +" of "+
                formatBytes(UploadActivity.Instance.totalSize)+"\n Total Files : "+this.splitFiles.length+" Uploaded : "+this.TotalUpload+" Failed : "+this.TotalUploadFailed);
            }
            
            return;
        }
        let triggerIndex = this.Index+nextTriggerCount;

        for(let i=this.Index+1;i<triggerIndex;i++){
            console.log("TriggerIndex : "+i);

            if(this.Index>=this.splitFiles.length-1)return;

            this.splitFiles[i].Upload();
            this.Index = i;
        }
    }

    SplitFilesBySize(){
        console.log("SplitFilesBySize File Count: "+this.files.length);
        
        let uploadZipFile = new UploadZipFile();
        
        for (let i = 0; i < this.files.length; i++) {
            let file = this.files[i],
            name = file.webkitRelativePath || file.name;
            let isFileAdded = false;  
            while(!isFileAdded){
                
                isFileAdded = uploadZipFile.AddFile(file);

                if(!isFileAdded && !uploadZipFile.IsFileComplete){
                    //Not able to handle large size file
                    //Handle separately.
                    isFileAdded = true;
                    continue;
                }

                if(uploadZipFile.IsFileComplete){
                    this.splitFiles.push(uploadZipFile);
                    uploadZipFile = new UploadZipFile();  
                    continue;
                }
            }

            this.totalSize += file.size;

        }
        console.log("SplitFilesBySize SplitFile Count: "+this.splitFiles.length);

    }
}

    
