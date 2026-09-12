/**
 * Ajapaik Rephoto Background Uploader
 * Uses IndexedDB to store photo uploads locally and runs them in the background
 */

class AjpDb {
  constructor() {
    this.dbName = 'AjpRephotoUploads';
    this.storeName = 'uploads';
    this.version = 1;
    this.db = null;
  }

  open() {
    return new Promise((resolve, reject) => {
      if (this.db) return resolve(this.db);
      
      const request = indexedDB.open(this.dbName, this.version);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };
      request.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName, { keyPath: 'id', autoIncrement: true });
        }
      };
    });
  }

  async getUploads() {
    const db = await this.open();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(this.storeName, 'readonly');
      const store = transaction.objectStore(this.storeName);
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async addUpload(upload) {
    const db = await this.open();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(this.storeName, 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.add(upload);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async updateUpload(upload) {
    const db = await this.open();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(this.storeName, 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.put(upload);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async deleteUpload(id) {
    const db = await this.open();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(this.storeName, 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.delete(id);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }
}

const AjpRephotoUploader = {
  db: new AjpDb(),
  currentXhr: null,
  currentUpload: null,
  retryTimer: null,
  isProcessing: false,

  init() {
    if (window.location.pathname.includes('/capture/')) {
      return;
    }
    this.injectStyles();
    this.processQueue();
    
    // Listen for network connection restoration
    window.addEventListener('online', () => {
      console.log('Network restored, processing upload queue...');
      this.processQueue();
    });
  },

  injectStyles() {
    if (document.getElementById('ajp-upload-styles')) return;
    const style = document.createElement('style');
    style.id = 'ajp-upload-styles';
    style.innerHTML = `
      .ajp-upload-widget {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 320px;
        background: rgba(34, 34, 34, 0.95);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.6);
        color: #fff;
        padding: 14px 16px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        z-index: 100000;
        display: flex;
        flex-direction: column;
        gap: 8px;
        transition: opacity 0.3s ease, transform 0.3s ease;
      }
      .ajp-upload-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        font-weight: 600;
      }
      .ajp-upload-title {
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .ajp-upload-status {
        font-size: 11px;
        color: #aaa;
      }
      .ajp-upload-progress-container {
        width: 100%;
        background: rgba(255, 255, 255, 0.1);
        height: 6px;
        border-radius: 3px;
        overflow: hidden;
      }
      .ajp-upload-progress-bar {
        height: 100%;
        background: #fca311;
        width: 0%;
        transition: width 0.1s ease;
      }
      .ajp-upload-actions {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
        margin-top: 4px;
        flex-wrap: wrap;
      }
      .ajp-upload-btn {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        color: #fff;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 11px;
        cursor: pointer;
        text-decoration: none;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        transition: background 0.2s;
      }
      .ajp-upload-btn:hover {
        background: rgba(255,255,255,0.18);
        text-decoration: none;
        color: #fff;
      }
      .ajp-upload-btn-primary {
        background: #fca311;
        border-color: #fca311;
        color: #000;
      }
      .ajp-upload-btn-primary:hover {
        background: #e5920f;
        color: #000;
      }
    `;
    document.head.appendChild(style);
  },

  async injectJpegComment(blob, commentString) {
    try {
      const arrayBuffer = await blob.arrayBuffer();
      const view = new DataView(arrayBuffer);
      
      if (arrayBuffer.byteLength < 4 || view.getUint16(0) !== 0xFFD8) {
        console.warn("Not a valid JPEG blob, skipping metadata injection");
        return blob;
      }
      
      const commentBytes = new TextEncoder().encode(commentString);
      const commentLength = commentBytes.length + 2;
      
      const marker = new Uint8Array(4 + commentBytes.length);
      marker[0] = 0xFF;
      marker[1] = 0xFE;
      marker[2] = (commentLength >> 8) & 0xFF;
      marker[3] = commentLength & 0xFF;
      marker.set(commentBytes, 4);
      
      const original = new Uint8Array(arrayBuffer);
      return new Blob([original.subarray(0, 2), marker, original.subarray(2)], { type: 'image/jpeg' });
    } catch (e) {
      console.error("Failed to inject JPEG comment:", e);
      return blob;
    }
  },

  async downloadUpload(uploadId) {
    try {
      const uploads = await this.db.getUploads();
      const upload = uploads.find(u => u.id === uploadId);
      if (!upload) {
        alert("Üleslaadimist ei leitud");
        return;
      }
      
      const url = URL.createObjectURL(upload.croppedBlob);
      const a = document.createElement('a');
      a.href = url;
      
      const authorId = upload.authorId || 'unknown';
      const scaleText = `scale-${upload.scaleFactor.toFixed(3)}`;
      a.download = `Ajapaik-rephotography-${authorId}-${upload.photoId}-${scaleText}.jpg`;
      
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Failed to download upload:", e);
      alert("Allalaadimine ebaõnnestus");
    }
  },

  async enqueue(authorId, photoId, photoSlug, fullBlob, croppedBlob, scaleFactor, uploadUrl, redirectUrl, lat, lon, yaw, pitch, roll) {
    const uploadId = `${Date.now()}_${authorId || 'anon'}_${photoId}_${Math.random().toString(36).substring(2, 8)}`;
    const upload = {
      uploadId,
      authorId,
      photoId,
      photoSlug,
      fullBlob,
      croppedBlob,
      scaleFactor,
      uploadUrl,
      redirectUrl,
      lat,
      lon,
      yaw,
      pitch,
      roll,
      status: 'pending',
      progress: 0,
      error: null,
      createdAt: Date.now()
    };
    await this.db.addUpload(upload);
    
    // Redirect immediately to prevent user blocking
    window.location.replace(redirectUrl);
  },

  async processQueue() {
    if (this.isProcessing) return;
    this.isProcessing = true;

    try {
      const uploads = await this.db.getUploads();
      
      // Sort oldest first
      uploads.sort((a, b) => a.createdAt - b.createdAt);
      
      const activeUpload = uploads.find(u => u.status === 'uploading' || u.status === 'pending' || u.status === 'failed');
      
      if (!activeUpload) {
        this.hideWidget();
        this.isProcessing = false;
        return;
      }

      this.currentUpload = activeUpload;
      this.showWidget(activeUpload);
      
      if (activeUpload.status === 'failed') {
        // Wait and retry automatically if failed, unless offline
        if (!navigator.onLine) {
          this.updateWidgetStatus(activeUpload, 'Võrguühendus puudub (oodatakse ühendust)');
          this.isProcessing = false;
          return;
        }
        
        this.updateWidgetStatus(activeUpload, 'Proovitakse uuesti...');
        await new Promise(resolve => setTimeout(resolve, 3000));
      }

      this.startUpload(activeUpload);
    } catch (err) {
      console.error('Error processing upload queue:', err);
      this.isProcessing = false;
    }
  },

  startUpload(upload) {
    upload.status = 'uploading';
    this.db.updateUpload(upload);
    this.updateWidgetProgress(0);
    this.updateWidgetStatus(upload, 'Üleslaadimine...');

    const xhr = new XMLHttpRequest();
    this.currentXhr = xhr;

    const formData = new FormData();
    formData.append('client_upload_id', upload.uploadId || `${upload.createdAt}_${upload.authorId}_${upload.photoId}`);
    formData.append('user_file[]', upload.fullBlob, 'rephoto.jpg');
    formData.append('cropped_file', upload.croppedBlob, 'rephoto_cropped.jpg');
    formData.append('scale_factor', upload.scaleFactor);
    if (upload.lat !== null && upload.lat !== undefined) {
      formData.append('lat', upload.lat);
    }
    if (upload.lon !== null && upload.lon !== undefined) {
      formData.append('lon', upload.lon);
    }
    if (upload.yaw !== null && upload.yaw !== undefined) {
      formData.append('yaw', upload.yaw);
    }
    if (upload.pitch !== null && upload.pitch !== undefined) {
      formData.append('pitch', upload.pitch);
    }
    if (upload.roll !== null && upload.roll !== undefined) {
      formData.append('roll', upload.roll);
    }

    xhr.open('POST', upload.uploadUrl, true);
    xhr.withCredentials = true; // Send session cookies

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        upload.progress = percent;
        this.updateWidgetProgress(percent);
      }
    });

    xhr.onload = async () => {
      this.currentXhr = null;
      if (xhr.status === 200) {
        try {
          const res = JSON.parse(xhr.responseText);
          if (res.error) {
            this.handleFailure(upload, res.error);
          } else {
            upload.newPhotoId = res.new_id;
            await this.handleSuccess(upload);
          }
        } catch (e) {
          this.handleFailure(upload, 'Serveri vastuse viga');
        }
      } else {
        this.handleFailure(upload, `Serveri viga (kood ${xhr.status})`);
      }
    };

    xhr.onerror = () => {
      this.currentXhr = null;
      this.handleFailure(upload, 'Ühenduse viga');
    };

    xhr.onabort = () => {
      this.currentXhr = null;
      this.isProcessing = false;
    };

    xhr.send(formData);
  },

  async handleSuccess(upload) {
    upload.status = 'success';
    await this.db.deleteUpload(upload.id);

    this.updateWidgetProgress(100);
    this.showSuccessWidget(upload);

    this.isProcessing = false;
    
    // Process next item in queue after 5 seconds (allows user to see success state)
    setTimeout(() => {
      this.processQueue();
    }, 5000);
  },

  handleFailure(upload, errorMessage) {
    upload.status = 'failed';
    upload.error = errorMessage;
    this.db.updateUpload(upload);

    this.showFailedWidget(upload, errorMessage);
    this.isProcessing = false;
  },

  cancelUpload(uploadId) {
    if (this.currentUpload && this.currentUpload.id === uploadId && this.currentXhr) {
      this.currentXhr.abort();
    }
    this.db.deleteUpload(uploadId).then(() => {
      this.hideWidget();
      this.processQueue();
    });
  },

  showWidget(upload) {
    let widget = document.getElementById('ajp-upload-widget');
    if (!widget) {
      widget = document.createElement('div');
      widget.id = 'ajp-upload-widget';
      widget.className = 'ajp-upload-widget';
      document.body.appendChild(widget);
    }

    widget.style.opacity = '1';
    widget.style.transform = 'translateY(0)';
    widget.innerHTML = `
      <div class="ajp-upload-header">
        <div class="ajp-upload-title">
          <span class="ajp-spinner-small" style="display:inline-block; width:12px; height:12px; border:2px solid #fca311; border-top-color:transparent; border-radius:50%; animation: ajp-spin 1s linear infinite;"></span>
          <b>Refoto üleslaadimine</b>
        </div>
        <div class="ajp-upload-status" id="ajp-upload-status-text">Ootel...</div>
      </div>
      <div class="ajp-upload-progress-container">
        <div class="ajp-upload-progress-bar" id="ajp-upload-progress-bar" style="width: ${upload.progress}%"></div>
      </div>
      <div class="ajp-upload-actions">
        <button class="ajp-upload-btn" onclick="AjpRephotoUploader.cancelUpload(${upload.id})">Tühista</button>
      </div>
    `;

    // Add spinner rotation animation if not present
    if (!document.getElementById('ajp-spin-style')) {
      const style = document.createElement('style');
      style.id = 'ajp-spin-style';
      style.innerHTML = '@keyframes ajp-spin { to { transform: rotate(360deg); } }';
      document.head.appendChild(style);
    }
  },

  updateWidgetStatus(upload, text) {
    const statusText = document.getElementById('ajp-upload-status-text');
    if (statusText) {
      statusText.innerText = text;
    }
  },

  updateWidgetProgress(percent) {
    const progressBar = document.getElementById('ajp-upload-progress-bar');
    if (progressBar) {
      progressBar.style.width = `${percent}%`;
    }
  },

  showSuccessWidget(upload) {
    const widget = document.getElementById('ajp-upload-widget');
    if (!widget) return;

    // Check if user is currently on the photo page of the uploaded photo
    const isOnPhotoPage = window.location.pathname.includes(`/photo/${upload.photoId}/`);
    let viewBtnHtml = '';
    if (upload.newPhotoId) {
      viewBtnHtml = `<a class="ajp-upload-btn ajp-upload-btn-primary" href="/photo/${upload.newPhotoId}/" style="text-decoration:none; display:inline-flex; align-items:center; justify-content:center;">Vaata refotot</a>`;
    } else if (isOnPhotoPage) {
      viewBtnHtml = `<button class="ajp-upload-btn ajp-upload-btn-primary" onclick="window.location.reload()">Värskenda lehte</button>`;
    }

    let returnListBtnHtml = '';
    let lastListUrl = null;
    try {
      lastListUrl = sessionStorage.getItem('lastRephotoListUrl');
    } catch (e) {}
    if (lastListUrl) {
      returnListBtnHtml = `<a class="ajp-upload-btn" href="${lastListUrl}" style="text-decoration:none; display:inline-flex; align-items:center; justify-content:center;">Tagasi lähimate fotode juurde</a>`;
    }

    widget.innerHTML = `
      <div class="ajp-upload-header" style="color: #4caf50;">
        <div class="ajp-upload-title">
          <span>✓</span>
          <b>Refoto edukalt salvestatud!</b>
        </div>
      </div>
      <div class="ajp-upload-progress-container">
        <div class="ajp-upload-progress-bar" style="width: 100%; background: #4caf50;"></div>
      </div>
      <div class="ajp-upload-actions">
        ${viewBtnHtml}
        ${returnListBtnHtml}
        <button class="ajp-upload-btn" onclick="AjpRephotoUploader.hideWidget()">Sulge</button>
      </div>
    `;

    // Auto-hide after 5 seconds if refresh button not clicked
    setTimeout(() => {
      if (widget && widget.style.opacity === '1' && !isOnPhotoPage) {
        this.hideWidget();
      }
    }, 5000);
  },

  showFailedWidget(upload, errorMessage) {
    const widget = document.getElementById('ajp-upload-widget');
    if (!widget) return;

    widget.innerHTML = `
      <div class="ajp-upload-header" style="color: #f44336;">
        <div class="ajp-upload-title">
          <span>⚠</span>
          <b>Viga salvestamisel</b>
        </div>
        <div class="ajp-upload-status" style="color: #f44336;">Tõrge</div>
      </div>
      <div style="font-size: 11px; color: #ccc;">${errorMessage}</div>
      <div class="ajp-upload-actions">
        <button class="ajp-upload-btn" onclick="AjpRephotoUploader.downloadUpload(${upload.id})">Salvesta seadmesse</button>
        <button class="ajp-upload-btn" onclick="AjpRephotoUploader.cancelUpload(${upload.id})">Kustuta järjekorrast</button>
        <button class="ajp-upload-btn ajp-upload-btn-primary" onclick="AjpRephotoUploader.processQueue()">Proovi uuesti</button>
      </div>
    `;
  },

  hideWidget() {
    const widget = document.getElementById('ajp-upload-widget');
    if (widget) {
      widget.style.opacity = '0';
      widget.style.transform = 'translateY(20px)';
      setTimeout(() => {
        if (widget.style.opacity === '0') {
          widget.remove();
        }
      }, 300);
    }
  }
};

// Start the uploader once the DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => AjpRephotoUploader.init());
} else {
  AjpRephotoUploader.init();
}
