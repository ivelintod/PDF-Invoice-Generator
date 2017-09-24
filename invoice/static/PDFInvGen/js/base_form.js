var total_forms = 1;

$(document).ready(function() {

    $(document).off().on('click', '.add-item-form', function(e){
        e.preventDefault();
        var form_template = $('.form-row:last').clone();
        $(form_template).find('input, textarea').each(function(){
            $(this).attr('id', $(this).attr('id').replace(total_forms - 1, total_forms));
            console.log($(this).attr('id'));
            $(this).val("");
        });
        total_forms += 1;
        $('#id_item-TOTAL_FORMS').attr('value', total_forms);
        $('.all-forms').append(form_template);
        return false;
    });

    $(document).on('click', '.remove-form-row', function(e){
        e.preventDefault();
        var form_to_remove = $('.form-row:last')
        $(form_to_remove).remove()
        total_forms -= 1
        $('#id_item-TOTAL_FORMS').attr('value', total_forms);
        return false;
    });

});
