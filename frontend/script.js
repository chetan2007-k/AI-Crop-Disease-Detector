/**
 * AI Crop Disease Detector - Frontend JavaScript
 * ================================================
 * Handles all frontend interactions:
 * - Image upload and preview
 * - API communication
 * - Results display
 * - User interface logic
 */

// =====================================================
// Configuration
// =====================================================

const API_URL = window.location.protocol === 'file:'
    ? 'http://localhost:5000'
    : window.location.origin;
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const previewContainer = document.getElementById('previewContainer');
const previewImage = document.getElementById('previewImage');
const removeBtn = document.getElementById('removeBtn');
const resultsSection = document.getElementById('resultsSection');
const loadingOverlay = document.getElementById('loadingOverlay');
const alertBox = document.getElementById('alertBox');
const alertMessage = document.getElementById('alertMessage');

let selectedFile = null;

// =====================================================
// Event Listeners
// =====================================================

// Browse button
browseBtn.addEventListener('click', () => {
    fileInput.click();
});

// File input change
fileInput.addEventListener('change', (e) => {
    const files = e.target.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// Remove image button
removeBtn.addEventListener('click', () => {
    resetUpload();
});

// Analyze button
analyzeBtn.addEventListener('click', () => {
    if (selectedFile) {
        analyzeDiseases();
    }
});

// New analysis button
document.getElementById('newAnalysisBtn').addEventListener('click', () => {
    resetUpload();
});

// Download report button
document.getElementById('downloadBtn').addEventListener('click', () => {
    downloadReport();
});

// =====================================================
// File Handling
// =====================================================

function handleFileSelect(file) {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!validTypes.includes(file.type)) {
        showAlert('Invalid file type. Please upload JPG, PNG, or GIF.', 'error');
        return;
    }

    // Validate file size (10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showAlert('File is too large. Maximum size is 10 MB.', 'error');
        return;
    }

    selectedFile = file;
    displayImagePreview(file);
}

function displayImagePreview(file) {
    // Create file reader
    const reader = new FileReader();
    
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewContainer.style.display = 'block';
        uploadArea.style.display = 'none';
        analyzeBtn.style.display = 'flex';
    };
    
    reader.readAsDataURL(file);
}

function resetUpload() {
    selectedFile = null;
    fileInput.value = '';
    previewContainer.style.display = 'none';
    uploadArea.style.display = 'block';
    analyzeBtn.style.display = 'none';
    resultsSection.style.display = 'none';
}

// =====================================================
// Disease Analysis
// =====================================================

async function analyzeDiseases() {
    if (!selectedFile) {
        showAlert('Please select an image first.', 'error');
        return;
    }

    // Show loading overlay
    loadingOverlay.style.display = 'flex';
    analyzeBtn.disabled = true;

    try {
        // Create FormData
        const formData = new FormData();
        formData.append('file', selectedFile);

        // Send request to backend
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            body: formData
        });

        // Parse response
        const result = await response.json();

        // Hide loading overlay
        loadingOverlay.style.display = 'none';
        analyzeBtn.disabled = false;

        // Check if prediction was successful
        if (result.success) {
            displayResults(result);
            showAlert('Disease analysis completed successfully!', 'success');
        } else {
            showAlert(result.error || 'Analysis failed. Please try again.', 'error');
        }
    } catch (error) {
        // Hide loading overlay
        loadingOverlay.style.display = 'none';
        analyzeBtn.disabled = false;

        console.error('Error:', error);
        showAlert('Error connecting to server. Make sure the backend is running.', 'error');
    }
}

// =====================================================
// Results Display
// =====================================================

function displayResults(data) {
    // Update disease name
    document.getElementById('diseaseName').textContent = `${data.crop} - ${data.disease.replace(/_/g, ' ')}`;

    // Update severity badge
    const severityBadge = document.getElementById('severity');
    const severityLevel = getSeverityLevel(data.severity);
    severityBadge.textContent = data.severity;
    severityBadge.className = `severity-badge ${severityLevel}`;

    // Update confidence
    const confidenceValue = parseFloat(data.confidence);
    document.getElementById('confidenceValue').textContent = `${confidenceValue.toFixed(2)}%`;
    document.getElementById('confidenceFill').style.width = `${Math.min(confidenceValue, 100)}%`;

    // Check if confidence is high enough
    if (confidenceValue < 60) {
        showAlert(`⚠️  Confidence is low (${confidenceValue.toFixed(1)}%). Results may be unreliable. Please take a clearer photo.`, 'warning');
    }

    // Update description
    document.getElementById('description').textContent = data.description;

    // Update treatment list
    const treatmentList = document.getElementById('treatmentList');
    treatmentList.innerHTML = '';
    data.treatment.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        treatmentList.appendChild(li);
    });

    // Update prevention list
    const preventionList = document.getElementById('preventionList');
    preventionList.innerHTML = '';
    data.prevention.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        preventionList.appendChild(li);
    });

    // Store current result for download
    window.currentResult = data;

    // Show results section
    resultsSection.style.display = 'block';

    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }, 100);
}

function getSeverityLevel(severity) {
    const level = severity.toLowerCase();
    if (level === 'none') return 'none';
    if (level === 'medium') return 'medium';
    if (level === 'high') return 'high';
    if (level.includes('very')) return 'very-high';
    return 'medium';
}

// =====================================================
// Report Download
// =====================================================

function downloadReport() {
    if (!window.currentResult) {
        showAlert('No results to download.', 'error');
        return;
    }

    const data = window.currentResult;
    const timestamp = new Date().toLocaleString();

    // Create report content
    let reportContent = `AI CROP DISEASE DETECTOR - ANALYSIS REPORT
========================================

Analysis Date: ${timestamp}

DISEASE IDENTIFICATION
---------------------
Crop: ${data.crop}
Disease: ${data.disease.replace(/_/g, ' ')}
Confidence: ${data.confidence}
Severity: ${data.severity}

DISEASE DESCRIPTION
-------------------
${data.description}

TREATMENT RECOMMENDATIONS
------------------------`;

    data.treatment.forEach((item, index) => {
        reportContent += `\n${index + 1}. ${item}`;
    });

    reportContent += `\n\nPREVENTION MEASURES
-----------------`;

    data.prevention.forEach((item, index) => {
        reportContent += `\n${index + 1}. ${item}`;
    });

    reportContent += `\n\n========================================
Generated by AI Crop Disease Detector
Website: http://localhost:5000
`;

    // Create blob and download
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `disease_report_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    showAlert('Report downloaded successfully!', 'success');
}

// =====================================================
// Alerts
// =====================================================

function showAlert(message, type = 'info') {
    alertMessage.textContent = message;
    alertBox.className = `alert ${type}`;
    alertBox.style.display = 'block';

    // Auto-hide after 5 seconds
    setTimeout(() => {
        closeAlert();
    }, 5000);
}

function closeAlert() {
    alertBox.style.display = 'none';
}

// =====================================================
// Backend Connectivity Check
// =====================================================

async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            console.log('✓ Backend is connected');
            
            if (!data.model_loaded) {
                showAlert('⚠️  Model is not loaded. Please train the model first.', 'warning');
            }
        }
    } catch (error) {
        console.error('Backend connection error:', error);
        showAlert('⚠️  Cannot connect to backend. Make sure the Flask server is running on localhost:5000', 'warning');
    }
}

// =====================================================
// Image Optimization Tips
// =====================================================

function showImageTips() {
    console.log(`
    📷 Tips for best results:
    1. Take clear, well-focused photos
    2. Ensure good natural lighting
    3. Zoom in on the diseased area
    4. Avoid shadows and glare
    5. Include the affected portion of the leaf
    6. Use a high-resolution camera
    `);
}

// =====================================================
// Initialization
// =====================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('AI Crop Disease Detector - Frontend Loaded');
    
    // Check backend connection
    setTimeout(checkBackendConnection, 1000);

    // Show tips in console
    showImageTips();

    // Enable smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// =====================================================
// Utility Functions
// =====================================================

function formatDiseaseName(name) {
    return name
        .replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Log app info
console.log(`
╔════════════════════════════════════════════════╗
║   AI CROP DISEASE DETECTOR - v1.0              ║
║   Frontend Application                          ║
╚════════════════════════════════════════════════╝

API Endpoint: ${API_URL}
For support, visit: http://localhost:5000

Features:
✓ Image Upload (JPG, PNG, GIF)
✓ Deep Learning Prediction
✓ Disease Identification
✓ Treatment Recommendations
✓ Report Download

Ready to analyze crop diseases!
`);
