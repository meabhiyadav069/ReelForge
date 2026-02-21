// ReelForge Application Logic

document.addEventListener('DOMContentLoaded', () => {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    const previewWindow = document.getElementById('preview-window');
    const videoWrapper = document.getElementById('video-preview-wrapper');
    const videoPlayer = document.getElementById('video-player');
    const generateBtn = document.getElementById('generate-btn');
    const processingOverlay = document.getElementById('processing-overlay');
    const statusText = document.getElementById('status-text');
    const substatusText = document.getElementById('substatus-text');
    const promptInput = document.getElementById('prompt-input');

    let selectedFile = null;

    // Trigger file input
    uploadZone.addEventListener('click', () => fileInput.click());

    // Drag and Drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('active');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('active');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('active');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    function handleFileSelection(file) {
        if (!file.type.startsWith('video/')) {
            alert('Please upload a video file.');
            return;
        }

        selectedFile = file;
        const url = URL.createObjectURL(file);

        // Update UI
        uploadZone.classList.add('hidden');
        videoWrapper.style.display = 'block';
        videoPlayer.src = url;
        videoPlayer.play();

        generateBtn.disabled = false;

        // Randomize prompt if empty
        if (!promptInput.value) {
            promptInput.value = "Create a high-energy cinematic reel with fast cuts and punchy captions.";
        }
    }

    generateBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        // Start processing simulation
        generateBtn.disabled = true;
        processingOverlay.style.display = 'flex';

        const steps = [
            { main: "Uploading to Gemini...", sub: "Moving bits to the cloud brain" },
            { main: "Analyzing Scenes...", sub: "AI is identifying peak engagement moments" },
            { main: "Crafting Hook...", sub: "Generating a viral 30-second script" },
            { main: "Applying Transitions...", sub: "Syncing frames to the rhythm" },
            { main: "Polishing Reel...", sub: "Color grading and final render" }
        ];

        for (const step of steps) {
            statusText.innerText = step.main;
            substatusText.innerText = step.sub;
            await new Promise(r => setTimeout(r, 1500));
        }

        // Finalize
        processingOverlay.style.display = 'none';

        // Show simulated transcript
        document.getElementById('transcript-container').style.display = 'block';
        document.getElementById('transcript-text').innerHTML = `
            <strong>[00:00]</strong> Hey everyone! Today we're diving into...<br>
            <strong>[00:05]</strong> Look at this amazing view from the top!<br>
            <strong>[00:12]</strong> Pro Tip: Always bring a spare battery.<br>
            <strong>[00:25]</strong> Thanks for watching, stay tuned for more!
        `;

        generateBtn.innerHTML = '<i data-lucide="download"></i> Download Reel';
        generateBtn.style.background = 'linear-gradient(to right, #10b981, #059669)';
        generateBtn.disabled = false;

        lucide.createIcons();

        confettiEffect();
    });

    function confettiEffect() {
        // Simple visual feedback
        const colors = ['#6366f1', '#a855f7', '#f43f5e'];
        for (let i = 0; i < 50; i++) {
            const div = document.createElement('div');
            div.style.position = 'fixed';
            div.style.width = '8px';
            div.style.height = '8px';
            div.style.background = colors[Math.floor(Math.random() * colors.length)];
            div.style.left = Math.random() * 100 + 'vw';
            div.style.top = '-10px';
            div.style.borderRadius = '50%';
            div.style.zIndex = '1000';
            div.style.pointerEvents = 'none';
            document.body.appendChild(div);

            const animation = div.animate([
                { transform: 'translateY(0) rotate(0deg)', opacity: 1 },
                { transform: `translateY(100vh) rotate(${Math.random() * 360}deg)`, opacity: 0 }
            ], {
                duration: 2000 + Math.random() * 3000,
                easing: 'cubic-bezier(0, .9, .57, 1)'
            });

            animation.onfinish = () => div.remove();
        }
    }
});
