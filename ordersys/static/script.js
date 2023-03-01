let item_id = 1;

document.addEventListener("click", (event) => {
    if (event.target.id.match(/item-\d+-del-btn/)) {
        const delid = event.target.id.split('-')[1];
        const delel = document.getElementById('item-' + delid);
        console.log(delel);
        delel.remove();
    }
});

const acheckEl = document.getElementById('all-check');
if (acheckEl) {
    acheckEl.addEventListener("change", (event) => {
        const pcheckEl = document.getElementById('project-check');
        if (acheckEl.checked == true) {
            pcheckEl.style.display = 'none';
        }
        else {
            pcheckEl.style.display = 'block';
        }
    })
}

const vendorEl = document.querySelector('[name="vendor"]');
if (vendorEl) {
    vendorEl.addEventListener('change', (event) => {
        if (event.target.value == 'Other') {
            document.getElementById('vendor-other').innerHTML =
                `<h6>If you answered <span class="badge text-bg-secondary">Other</span> as your vendor</h6>
                <div class="col-md-8">
                    <label for="vendor-other-name" class="form-label">Name of Vendor</label>
                    <input class="form-control" name="vendor-other-name" id="vendor-other-name" required>
                </div>
                <div class="col-md-8 mb-3">
                    <label for="vendor-other-url" class="form-label">Web Address of Vendor</label>
                    <div class="input-group">
                        <div class="input-group-prepend">
                            <div style="border-top-right-radius:0;border-bottom-right-radius:0;" class="input-group-text">www.</div>
                        </div>
                        <input class="form-control" name="vendor-other-url" id="vendor-other-url" required>
                    </div>
                </div>`;
        }
        else {
            document.getElementById('vendor-other').innerHTML = '';
        }
    });
}

const newitemEl = document.querySelector('#new-item-btn');
if (newitemEl) {
    newitemEl.addEventListener('click', (event) => {
        item_id++;
        
        const itemDiv = document.getElementById('items');
        
        var newItem = document.createElement('div');
        newItem.setAttribute('id', 'item-' + item_id);
        newItem.setAttribute('class', 'col-md-8');
        newItem.innerHTML = 
            `<div class="card mt-3 item-${item_id}">
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-12">
                            <h5>Item #${item_id}</h5>
                        </div>
                        <div class="col-md-12">
                            <label for="item-description-${item_id}" class="form-label">Description</label>
                            <input class="form-control" name="item-description-${item_id}" id="item-description-${item_id}" required>
                        </div>
                        <div class="col-md-12 mb-2">
                            <label for="item-number-${item_id}" class="form-label">Part Number</label>
                            <input class="form-control" name="item-number-${item_id}" id="item-number-${item_id}" required>
                        </div>
                        <div class="col-md-12 mb-2">
                            <label for="item-price-${item_id}" class="form-label">Price Per Unit</label>
                            <div class="input-group">
                                <div class="input-group-prepend">
                                    <div style="border-top-right-radius:0;border-bottom-right-radius:0;" class="input-group-text">$</div>
                                </div>
                                <input step="0.01"  type="number" class="form-control" name="item-price-${item_id}" id="item-price-${item_id}" required>
                            </div>
                        </div>
                        <div class="col-md-12">
                            <label for="item-quantity-${item_id}" class="form-label">Quantity</label>
                            <input min="1" step="1" type="number" class="form-control" name="item-quantity-${item_id}" id="item-quantity-${item_id}" required>
                        </div>
                        <div class="col-md-12 mb-2">
                            <label for="item-justification-${item_id}" class="form-label">Justification</label>
                            <textarea class="form-control" name="item-justification-${item_id}" id="item-justification-${item_id}" required></textarea>
                        </div>
                        <div class="col-md-12 mb-2">
                            <button id="item-${item_id}-del-btn" class="mt-0 btn btn-danger">
                                Delete Item
                            </button>
                        </div>
                    </div>
                </div>
            </div> `;
        
        itemDiv.appendChild(newItem);
    });
}