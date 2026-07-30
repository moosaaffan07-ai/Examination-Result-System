document.addEventListener('DOMContentLoaded', () => {
    // ── Live Calculation Preview in Form ──
    const englishInput = document.getElementById('english');
    const mathsInput = document.getElementById('maths');
    const scienceInput = document.getElementById('science');

    const previewTotal = document.getElementById('preview-total');
    const previewPercentage = document.getElementById('preview-percentage');
    const previewGrade = document.getElementById('preview-grade');
    const previewStatus = document.getElementById('preview-status');

    function calculateGrade(percentage) {
        if (percentage >= 90) return 'A+';
        if (percentage >= 80) return 'A';
        if (percentage >= 70) return 'B';
        if (percentage >= 60) return 'C';
        if (percentage >= 50) return 'D';
        return 'F';
    }

    function updateLivePreview() {
        if (!englishInput || !mathsInput || !scienceInput) return;

        const eng = parseFloat(englishInput.value) || 0;
        const mat = parseFloat(mathsInput.value) || 0;
        const sci = parseFloat(scienceInput.value) || 0;

        const hasValues = englishInput.value !== '' || mathsInput.value !== '' || scienceInput.value !== '';

        if (!hasValues) {
            if (previewTotal) previewTotal.textContent = '—';
            if (previewPercentage) previewPercentage.textContent = '—%';
            if (previewGrade) {
                previewGrade.textContent = '—';
                previewGrade.className = 'grade-pill';
            }
            if (previewStatus) {
                previewStatus.textContent = '—';
                previewStatus.className = 'status-badge';
            }
            return;
        }

        const total = Math.round((eng + mat + sci) * 100) / 100;
        const percentage = Math.round((total / 3) * 10) / 10;
        const grade = calculateGrade(percentage);
        const isPass = percentage >= 50;
        const statusText = isPass ? 'Pass' : 'Fail';

        if (previewTotal) previewTotal.textContent = total;
        if (previewPercentage) previewPercentage.textContent = `${percentage}%`;
        if (previewGrade) {
            previewGrade.textContent = grade;
            const safeGrade = grade.replace('+', 'plus');
            previewGrade.className = `grade-pill grade-${safeGrade}`;
        }
        if (previewStatus) {
            previewStatus.textContent = statusText;
            previewStatus.className = `status-badge status-${statusText.toLowerCase()}`;
        }
    }

    if (englishInput && mathsInput && scienceInput) {
        [englishInput, mathsInput, scienceInput].forEach(input => {
            input.addEventListener('input', updateLivePreview);
        });
        updateLivePreview();
    }

    // ── Auto-dismiss Toast Notifications ──
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.className = 'toast-close';
        closeBtn.setAttribute('aria-label', 'Close notification');
        closeBtn.onclick = () => fadeAndRemove(toast);
        toast.appendChild(closeBtn);

        setTimeout(() => {
            fadeAndRemove(toast);
        }, 5000);
    });

    function fadeAndRemove(el) {
        el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        el.style.opacity = '0';
        el.style.transform = 'translateY(-10px)';
        setTimeout(() => el.remove(), 400);
    }

    // ── Client-side Instant Filter on Table ──
    const filterInput = document.querySelector('input[name="q"]');
    const tableRows = document.querySelectorAll('.data-table tbody tr');

    if (filterInput && tableRows.length > 0) {
        filterInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }

    // ── Print Report Handler ──
    const printBtn = document.getElementById('print-report-btn');
    if (printBtn) {
        printBtn.addEventListener('click', () => {
            window.print();
        });
    }
});
