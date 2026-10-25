/**
 * Smart Food Waste Reduction System
 * Frontend interactive utilities and UI enhancements
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto-dismiss flash alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });

    // 2. Client-side quick search/filter on tables
    const tableSearchInput = document.getElementById('tableSearchInput');
    if (tableSearchInput) {
        tableSearchInput.addEventListener('keyup', function () {
            const filter = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('.filterable-table tbody tr');
            tableRows.forEach(function (row) {
                const text = row.textContent.toLowerCase();
                if (text.indexOf(filter) > -1) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // 3. Purchase date and expiry date helper
    const purchaseDateInput = document.getElementById('purchase_date');
    const expiryDateInput = document.getElementById('expiry_date');
    const categorySelect = document.getElementById('category');

    // Default shelf life days by category for quick guidance
    const categoryDefaultShelfLife = {
        'Fruits & Vegetables': 7,
        'Dairy & Eggs': 10,
        'Bakery': 5,
        'Meat & Poultry': 3,
        'Seafood': 2,
        'Grains & Cereals': 90,
        'Prepared Meals': 4,
        'Beverages': 14,
        'Pantry & Condiments': 180,
        'Snacks': 60
    };

    if (purchaseDateInput && !purchaseDateInput.value) {
        const todayStr = new Date().toISOString().split('T')[0];
        purchaseDateInput.value = todayStr;
    }

    if (categorySelect && expiryDateInput && purchaseDateInput) {
        categorySelect.addEventListener('change', function () {
            const selectedCategory = this.value;
            const daysToAdd = categoryDefaultShelfLife[selectedCategory];
            if (daysToAdd && !expiryDateInput.value) {
                const baseDate = new Date(purchaseDateInput.value || new Date());
                baseDate.setDate(baseDate.getDate() + daysToAdd);
                expiryDateInput.value = baseDate.toISOString().split('T')[0];
            }
        });
    }

    // 4. Populate Waste Modal when logging waste from inventory
    const wasteModal = document.getElementById('logWasteModal');
    if (wasteModal) {
        wasteModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (!button) return;
            const itemId = button.getAttribute('data-item-id');
            const itemName = button.getAttribute('data-item-name');
            const itemQty = button.getAttribute('data-item-qty');
            const itemUnit = button.getAttribute('data-item-unit');
            const formAction = button.getAttribute('data-action');

            const modalItemName = wasteModal.querySelector('#modalWasteFoodName');
            const modalForm = wasteModal.querySelector('#wasteModalForm');

            if (modalItemName) modalItemName.textContent = itemName + " (" + itemQty + " " + itemUnit + ")";
            if (modalForm && formAction) modalForm.action = formAction;
        });
    }

    // 5. Populate Quick Donation Modal
    const donationModal = document.getElementById('quickDonateModal');
    if (donationModal) {
        donationModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (!button) return;
            const itemId = button.getAttribute('data-item-id');
            const itemName = button.getAttribute('data-item-name');
            const itemCategory = button.getAttribute('data-item-category');
            const itemQty = button.getAttribute('data-item-qty');
            const itemUnit = button.getAttribute('data-item-unit');

            const idInput = donationModal.querySelector('#modal_inventory_item_id');
            const nameInput = donationModal.querySelector('#modal_food_name');
            const catInput = donationModal.querySelector('#modal_category');
            const qtyInput = donationModal.querySelector('#modal_quantity');
            const unitInput = donationModal.querySelector('#modal_unit');

            if (idInput) idInput.value = itemId || '';
            if (nameInput) nameInput.value = itemName || '';
            if (catInput) catInput.value = itemCategory || 'Fruits & Vegetables';
            if (qtyInput) qtyInput.value = itemQty || '1';
            if (unitInput) unitInput.value = itemUnit || 'kg';
        });
    }
});
