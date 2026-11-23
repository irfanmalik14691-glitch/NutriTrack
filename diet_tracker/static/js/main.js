/**
 * NutriTrack 3D - Main UI Logic & Micro-interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Sidebar Controls
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    const closeBtn = document.getElementById('sidebarClose');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.add('open');
        });
    }

    if (closeBtn && sidebar) {
        closeBtn.addEventListener('click', () => {
            sidebar.classList.remove('open');
        });
    }

    // Close sidebar on outer click for mobile
    document.addEventListener('click', (e) => {
        if (sidebar && sidebar.classList.contains('open')) {
            if (!sidebar.contains(e.target) && (!toggleBtn || !toggleBtn.contains(e.target))) {
                sidebar.classList.remove('open');
            }
        }
    });

    // 2. Auto-dismiss Flash Alerts
    const alerts = document.querySelectorAll('.flash-alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = 'all 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // 3. Dynamic Grams to Macro Calculator in Food Modals/Forms
    const foodSelect = document.getElementById('food_item_select');
    const gramsInput = document.getElementById('quantity_grams_input');

    if (foodSelect && gramsInput) {
        function updateFoodPreview() {
            const selectedOpt = foodSelect.options[foodSelect.selectedIndex];
            if (!selectedOpt || !selectedOpt.dataset.cal) return;

            const grams = parseFloat(gramsInput.value) || 0;
            const ratio = grams / 100.0;

            const cal100 = parseFloat(selectedOpt.dataset.cal) || 0;
            const p100 = parseFloat(selectedOpt.dataset.protein) || 0;
            const c100 = parseFloat(selectedOpt.dataset.carbs) || 0;
            const f100 = parseFloat(selectedOpt.dataset.fat) || 0;

            // Update hidden inputs if present
            const hCal = document.getElementById('hidden_cal_100');
            const hP = document.getElementById('hidden_p_100');
            const hC = document.getElementById('hidden_c_100');
            const hF = document.getElementById('hidden_f_100');
            const hName = document.getElementById('hidden_food_name');

            if (hCal) hCal.value = cal100;
            if (hP) hP.value = p100;
            if (hC) hC.value = c100;
            if (hF) hF.value = f100;
            if (hName) hName.value = selectedOpt.dataset.name || selectedOpt.text;

            // Update live preview indicators
            const previewCal = document.getElementById('preview_calories');
            const previewP = document.getElementById('preview_protein');
            const previewC = document.getElementById('preview_carbs');
            const previewF = document.getElementById('preview_fat');

            if (previewCal) previewCal.textContent = (cal100 * ratio).toFixed(1) + ' kcal';
            if (previewP) previewP.textContent = (p100 * ratio).toFixed(1) + 'g';
            if (previewC) previewC.textContent = (c100 * ratio).toFixed(1) + 'g';
            if (previewF) previewF.textContent = (f100 * ratio).toFixed(1) + 'g';
        }

        foodSelect.addEventListener('change', updateFoodPreview);
        gramsInput.addEventListener('input', updateFoodPreview);
        updateFoodPreview();
    }

    // 4. Quick Water Add Buttons
    const quickWaterBtns = document.querySelectorAll('.quick-water-btn');
    const waterAmountInput = document.getElementById('water_amount_input');
    if (quickWaterBtns && waterAmountInput) {
        quickWaterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const addMl = parseInt(btn.dataset.ml) || 250;
                waterAmountInput.value = addMl;
                // auto submit form
                const form = document.getElementById('water_log_form');
                if (form) form.submit();
            });
        });
    }
});
