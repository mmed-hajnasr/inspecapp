let dataTable;
let currentEditingRow = -1;

// Define certifications array globally
const QUALIFICATIONS = {
  1: ['MED', 'LIC', 'ATO', 'TRTO', 'FSTD', 'MA', 'GN', 'AO', 'RANPF', 'RANPN'],
  2: ['INFR', 'AIDs', 'SSLIA'],
  3: ['ATS', 'MET', 'AIS/AIM', 'SAR', 'PANS-OPS', 'MAP', 'CNS']
};

// Function to generate checkbox grid
function generateCheckboxGrid(formPrefix, type = '1') {
  const grid = document.createElement('div');
  grid.className = 'checkbox-grid';
  
  const certifications = QUALIFICATIONS[type] || [];
  
  certifications.forEach(cert => {
    const item = document.createElement('div');
    item.className = 'checkbox-item';
    
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.id = `${formPrefix}-${cert.toLowerCase()}`;
    input.name = cert;
    
    const label = document.createElement('label');
    label.htmlFor = input.id;
    label.textContent = cert;
    
    item.appendChild(input);
    item.appendChild(label);
    grid.appendChild(item);
  });
  
  return grid;
}

$(document).ready(function () {
  // Initial checkbox grids for add and edit forms
  const addFormGrid = generateCheckboxGrid('add', '1');
  const editFormGrid = generateCheckboxGrid('edit', '1');
  
  $('#add-form-certifications').html(addFormGrid.outerHTML);
  $('#edit-form-certifications').html(editFormGrid.outerHTML);

  // Update checkboxes when type changes
  $('#add-type').change(function() {
    const type = $(this).val();
    const newGrid = generateCheckboxGrid('add', type);
    $('#add-form-certifications').html(newGrid.outerHTML);
  });

  $('#edit-type').change(function() {
    const type = $(this).val();
    const newGrid = generateCheckboxGrid('edit', type);
    $('#edit-form-certifications').html(newGrid.outerHTML);
  });
  document.title = "Inspector Data Table";
  
  // Load data from Python backend
  loadTableData();
  
  // Add button click handler
  $(document).on('click', '.dt-add', function() {
    $('#addModal').modal('show');
  });
  
  // Edit button click handler
  $(document).on('click', '.dt-edit', function() {
    const row = $(this).closest('tr');
    const rowIndex = dataTable.row(row).index();
    currentEditingRow = rowIndex;
    
    // Get original data from backend
    eel.get_row_data(rowIndex)(function(rowData) {
      if (rowData) {
        populateEditForm(rowData);
        $('#editModal').modal('show');
      }
    });
  });
  
  // Delete button click handler
  $(document).on('click', '.dt-delete', function() {
    const row = $(this).closest('tr');
    const rowData = dataTable.row(row).data();
    currentEditingRow = dataTable.row(row).index();
    
    if (confirm('Are you sure you want to delete this inspector?')) {
      eel.delete_row(currentEditingRow)(function(success) {
        if (success) {
          loadTableData();
        } else {
          alert('Error deleting inspector');
        }
      });
    }
  });

  // Print card button click handler
  $(document).on('click', '.dt-print', function() {
    const row = $(this).closest('tr');
    const rowIndex = dataTable.row(row).index();
    eel.print_card(rowIndex)();
  });

  
  // Save changes button
  $('#saveChanges').click(async function() {
    const formData = await getFormData('editForm');
    
    eel.update_row(currentEditingRow, formData)(function(success) {
      if (success) {
        $('#editModal').modal('hide');
        loadTableData(); // Reload table
      } else {
        alert('Error updating inspector');
      }
    });
  });
  
  // Add inspector button
  $('#addInspector').click(async function() {
    const formData = await getFormData('addForm');
    
    if (!formData.surname || !formData.name) {
      alert('Surname and Name are required');
      return;
    }
    
    eel.add_new_row(formData)(function(success) {
      if (success) {
        $('#addModal').modal('hide');
        clearForm('addForm');
        loadTableData(); // Reload table
      } else {
        alert('Error adding inspector');
      }
    });
  });
  
  // Clear forms when modals are hidden
  $('#addModal').on('hidden.bs.modal', function() {
    clearForm('addForm');
  });
  
  $('#editModal').on('hidden.bs.modal', function() {
    clearForm('editForm');
  });
});

function loadTableData() {
  eel.get_table_data()(function(data) {
    if (dataTable) {
      dataTable.destroy();
    }
    
    const tableData = data.map((row, index) => {
      // Add timestamp to prevent caching
      const timestamp = new Date().getTime();
      const imageSrc = `/data/images/${row.id}.png?t=${timestamp}`;
      const imageCell = `
        <div class="image-cell">
          <img src="${imageSrc}" 
               onerror="this.onerror=null;this.src='/data/images/No_image.png'" 
               alt="Inspector Image" 
               style="width: 50px; height: 50px; object-fit: cover;">
        </div>
      `;
      return [
        imageCell,
        row.nb,
        row.surname,
        row.name,
        row.date_of_issue,
        row.date_of_expiry,
        row.id,
        row.type === '1' ? 'OPS' : row.type === '2' ? 'AGA' : row.type === '3' ? 'ANS' : '',
        `<button type="button" class="btn btn-primary btn-xs dt-edit" style="margin-right:8px;">
           <span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>
         </button>
         <button type="button" class="btn btn-danger btn-xs dt-delete" style="margin-right:8px;">
           <span class="glyphicon glyphicon-remove" aria-hidden="true"></span>
         </button>
         <button type="button" class="btn btn-info btn-xs dt-print">
           <span class="glyphicon glyphicon-print" aria-hidden="true"></span>
         </button>`
      ];
    });
    
    dataTable = $("#example").DataTable({
      data: tableData,
      dom: '<"dt-buttons"Bf><"clear">lirtp',
      paging: true,
      pageLength: 25,
      autoWidth: true,
      columnDefs: [
        { orderable: false, targets: 8 }
      ],
      buttons: [
        "colvis",
        "copyHtml5",
        "csvHtml5",
        "excelHtml5",
        "pdfHtml5"
      ]
    });
  });
}

// Preview image when selected
function previewImage(input, previewId) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = function(e) {
      $(previewId).attr('src', e.target.result);
    };
    reader.readAsDataURL(input.files[0]);
  }
}

// Add image preview handlers
$(document).ready(function() {
  $('#add-image').change(function() {
    previewImage(this, '#add-image-preview');
  });

  $('#edit-image').change(function() {
    previewImage(this, '#edit-image-preview');
  });
});

function populateEditForm(rowData) {
  $('#edit-nb').val(rowData.nb);
  $('#edit-surname').val(rowData.surname);
  $('#edit-name').val(rowData.name);
  $('#edit-date-issue').val(rowData.date_of_issue);
  $('#edit-date-expiry').val(rowData.date_of_expiry);
  $('#edit-id').val(rowData.id);
  $('#edit-type').val(rowData.type);
  
  // Set placeholders with original data
  $('#edit-nb').attr('placeholder', rowData.nb);
  $('#edit-surname').attr('placeholder', rowData.surname);
  $('#edit-name').attr('placeholder', rowData.name);
  $('#edit-date-issue').attr('placeholder', rowData.date_of_issue || 'DD/MM/YYYY');
  $('#edit-date-expiry').attr('placeholder', rowData.date_of_expiry || 'DD/MM/YYYY');
  $('#edit-id').attr('placeholder', rowData.id);
  $('#edit-type').attr('placeholder', rowData.type);

  // Set current image with timestamp to prevent caching
  const timestamp = new Date().getTime();
  const imageSrc = `/data/images/${rowData.id}.png?t=${timestamp}`;
  $('#edit-image-preview').attr('src', imageSrc)
    .on('error', function() {
      $(this).attr('src', '/data/images/No_image.png');
    });
  
  // First update the grid with the correct type's checkboxes
  const newGrid = generateCheckboxGrid('edit', rowData.type);
  $('#edit-form-certifications').html(newGrid.outerHTML);
  
  // Then set the checkbox values based on the data
  const certifications = QUALIFICATIONS[rowData.type] || [];
  certifications.forEach(cert => {
    if (rowData[cert] === 'X') {
      $(`#edit-${cert.toLowerCase()}`).prop('checked', true);
    }
  });
}

async function getFormData(formId) {
  const formData = {};
  const form = $('#' + formId);
  
  // Get text inputs and select values
  form.find('input[type="text"], select').each(function() {
    formData[$(this).attr('name')] = $(this).val();
  });
  
  // Get checkboxes
  form.find('input[type="checkbox"]').each(function() {
    formData[$(this).attr('name')] = $(this).is(':checked') ? 'X' : '';
  });
  
  // Get file input
  const imageInput = form.find('input[type="file"]')[0];
  if (imageInput && imageInput.files.length > 0) {
    const file = imageInput.files[0];
    const reader = new FileReader();
    
    // Convert file to base64
    const base64Promise = new Promise((resolve) => {
      reader.onload = (e) => resolve(e.target.result);
    });
    reader.readAsDataURL(file);
    
    formData.image = await base64Promise;
  }
  
  return formData;
}

function clearForm(formId) {
  const form = $('#' + formId);
  form.find('input[type="text"], select').val('');
  form.find('input[type="checkbox"]').prop('checked', false);
}
