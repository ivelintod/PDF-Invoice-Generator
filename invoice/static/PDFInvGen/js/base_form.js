var total_forms = parseInt($('#id_item-TOTAL_FORMS').val());

function addForm() {
    var form_template = $('.form-row:last').clone();
    $(form_template).find('input, textarea, label').each(function(ind, obj) {
        ['id', 'name', 'for'].forEach(function(attr) {
            if ($(obj).attr(attr)) {
                $(obj).attr(attr, $(obj).attr(attr).replace(total_forms - 1, total_forms));
            }
        });
        $(this).val('');
    });
    total_forms += 1;
    $('#id_item-TOTAL_FORMS').attr('value', total_forms);
    $('.all-forms').append(form_template);
}

function removeForm() {
    var form_to_remove = $('.form-row:last');
    $(form_to_remove).remove();
    total_forms -= 1;
    $('#id_item-TOTAL_FORMS').attr('value', total_forms);
    $('.form-row').each(function(ind, obj) {
        $(obj).find('input', 'textarea', 'label').each(function(inner_ind, inner_obj) {
            var id_regex = new RegExp('\\d{1}');
            ['id', 'name', 'for'].forEach(function(attr) {
                if ($(inner_obj).attr(attr)) {
                    $(inner_obj).attr(attr, $(inner_obj).attr(attr).replace(id_regex, ind));
                }
            });
        });
    });
}

$(document).ready(function() {
    $(document).off().on('click', '.add-item-form', function(e) {
        e.preventDefault();
        addForm();
        return false;
    });

    $(document).on('click', '.remove-form-row', function(e) {
        e.preventDefault();
        removeForm();
        return false;
    });
});
