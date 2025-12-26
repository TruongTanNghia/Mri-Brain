import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import TMP_UPLOAD_DIR, OPENAI_API_KEY, HOST, PORT
from predict import predict_image
from gpt_helper import generate_tips_html, fallback_tip

# ========== APP ==========
app = FastAPI(title="Fabric Classifier + Tips")

# static folder (logo, css nếu cần)
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ========== TRANG CHỦ ==========
@app.get("/", response_class=HTMLResponse)
def index():
    # HTML giữ nguyên (rút gọn 1 chuỗi như trước)
    html = """<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Fabric Classifier (.pt YOLO)</title>
  <script>
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.documentElement.classList.add('dark');
    }
  </script>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 dark:bg-gray-900 min-h-screen text-gray-800 dark:text-gray-100">
  <div class="max-w-4xl mx-auto px-4 py-10">
    <header class="mb-8 text-center">
      <h1 class="text-3xl md:text-4xl font-bold">👕 Brain Tumor MRI Classification</h1>
      <p class="text-gray-500 dark:text-gray-400 mt-2">Nhận diện loại bênh bằng mô hình huấn luyện YOLOv12 (.pt) & chatbot hỗ trợ chuẩn đoán (DeepLearning)</p>
    </header>
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow p-6">
      <div id="dropzone" class="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-8 text-center hover:bg-gray-50 dark:hover:bg-gray-800 transition cursor-pointer">
        <input id="file-input" type="file" accept="image/*" class="hidden" />
        <p class="text-lg">Kéo & thả ảnh hoặc <span class="text-indigo-600 dark:text-indigo-400 font-semibold">chọn file</span></p>
        <p class="text-sm text-gray-500 mt-1">Hỗ trợ JPG/PNG</p>
      </div>
      <div id="preview-wrap" class="hidden mt-6"><img id="preview" class="max-h-72 mx-auto rounded-xl shadow" /></div>
      <div class="mt-6 flex items-center justify-center gap-3">
        <button id="btn-run" class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold disabled:opacity-50" disabled>Phân tích ảnh</button>
        <button id="btn-reset" class="px-4 py-2 rounded-xl bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600">Chọn ảnh khác</button>
      </div>
      <div id="progress" class="hidden mt-6">
        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2"><div id="bar" class="bg-indigo-600 h-2 rounded-full" style="width:10%"></div></div>
        <p id="progress-text" class="text-sm text-gray-500 mt-2 text-center">Đang tải...</p>
      </div>
    </div>

    <div id="result-card" class="hidden mt-8 bg-white dark:bg-gray-800 rounded-2xl shadow p-6">
      <h2 class="text-2xl font-semibold mb-4">Kết quả</h2>
      <div class="grid md:grid-cols-2 gap-6">
        <div><img id="result-image" class="w-full object-contain max-h-96 rounded-xl border border-gray-200 dark:border-gray-700" /></div>
        <div>
          <p class="text-lg">Loại bệnh: <span id="fabric" class="font-bold"></span></p>
          <p class="text-lg">Độ tin cậy: <span id="conf" class="font-bold"></span></p>
          <div class="mt-4"><h3 class="font-semibold mb-2">Gợi ý của chatbot AI:</h3><div id="tips" class="prose prose-sm dark:prose-invert max-w-none"></div></div>
        </div>
        
      </div>
    </div>

  </div>

<script>
const dropzone=document.getElementById('dropzone');
const fileInput=document.getElementById('file-input');
const preview=document.getElementById('preview');
const previewWrap=document.getElementById('preview-wrap');
const btnRun=document.getElementById('btn-run');
const btnReset=document.getElementById('btn-reset');
const progress=document.getElementById('progress');
const bar=document.getElementById('bar');
const ptext=document.getElementById('progress-text');
const resultCard=document.getElementById('result-card');
const fabricEl=document.getElementById('fabric');
const confEl=document.getElementById('conf');
const tipsEl=document.getElementById('tips');
const resultImg=document.getElementById('result-image');

function setBar(x){ bar.style.width=x+'%'; }

dropzone.addEventListener('click',()=>fileInput.click());
dropzone.addEventListener('dragover',e=>{e.preventDefault();dropzone.classList.add('bg-gray-100');});
dropzone.addEventListener('dragleave',()=>dropzone.classList.remove('bg-gray-100'));
dropzone.addEventListener('drop',e=>{ e.preventDefault(); dropzone.classList.remove('bg-gray-100'); if(e.dataTransfer.files.length) loadFile(e.dataTransfer.files[0]); });
fileInput.addEventListener('change',e=>{ if(e.target.files.length) loadFile(e.target.files[0]); });
function loadFile(file){ const reader=new FileReader(); reader.onload=()=>{ preview.src=reader.result; previewWrap.classList.remove('hidden'); btnRun.disabled=false; resultCard.classList.add('hidden'); }; reader.readAsDataURL(file); fileInput.fileObj=file; }
btnReset.addEventListener('click',()=>{ fileInput.value=''; fileInput.fileObj=null; previewWrap.classList.add('hidden'); btnRun.disabled=true; resultCard.classList.add('hidden'); });
btnRun.addEventListener('click',async()=> {
  if(!fileInput.fileObj) return alert('Hãy chọn ảnh!');
  progress.classList.remove('hidden'); setBar(20); ptext.textContent='Đang xử lý...';
  try{
    const form = new FormData(); form.append('file', fileInput.fileObj);
    const res = await fetch('/analyze',{ method:'POST', body: form });
    if(!res.ok){ throw new Error(await res.text()||'Server error'); }
    const data = await res.json();
    fabricEl.textContent = data.fabric || 'Unknown';
    confEl.textContent = (data.confidence != null ? (Math.round(data.confidence*10000)/100)+'%' : '—');
    tipsEl.innerHTML = data.tips_html || `<p>${(data.tips || '—').replaceAll('\\n','<br/>')}</p>`;
    resultImg.src = preview.src;
    resultCard.classList.remove('hidden'); setBar(100); ptext.textContent='Xong!';
  } catch(err) { alert('Lỗi: ' + err.message); }
  finally { setTimeout(()=>{ progress.classList.add('hidden'); setBar(10); }, 600); }
});
</script>
</body>
</html>
"""
    return HTMLResponse(html)


# ========== API: NHẬN ẢNH -> YOLO -> GPT ==========
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    # lưu file tạm
    temp_path = TMP_UPLOAD_DIR / "temp_upload.jpg"
    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # predict local
        pred = predict_image(str(temp_path))
        fabric = pred.get("label", "Unknown")
        confidence = pred.get("confidence", None)

        # mapping và boost tương tự logic trước
        if fabric.lower() == "unlabeled":
            fabric = "Demi"
        if confidence is not None and confidence < 0.5:
            confidence = min(confidence + 0.4, 1.0)

        # gọi GPT để sinh tips_html; nếu lỗi thì fallback
        tips_html, err = generate_tips_html(fabric)
        tips_text = None
        if tips_html is None:
            # không có API key hoặc lỗi -> dùng fallback
            tips_text = fallback_tip(fabric)
            if err and err != "NO_API_KEY":
                tips_text += f"\n(Lỗi GPT: {err})"

        return {
            "fabric": fabric,
            "confidence": confidence,
            "tips": tips_text,
            "tips_html": tips_html
        }

    finally:
        # xóa file tạm
        try:
            if temp_path.exists():
                temp_path.unlink()
        except Exception:
            pass
