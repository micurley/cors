$(document).ready(function(){
    var base_href = document.domain;
    $.each($('.base-href'), function(){
        $(this).html(base_href);
    })

    function addCodemirror(container, data){
        var myCodeMirror = CodeMirror(container, {
            mode:  "javascript",
            lineNumbers: true,
            foldGutter: true,
            gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
        });           
        
        myCodeMirror.setValue(JSON.stringify(data, null, '  '));
    }

    $.each($('.example'), function(index, value){
        var container = this;
        var link = $(container).find('a');
        $.get(link.attr('href'), 
            function(data) {
                addCodemirror(container, data);
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                data = {
                    'jqXHR': jqXHR,
                    'textStatus': textStatus,
                    'errorThrown': errorThrown,
                };
                addCodemirror(container, data);
            });
    }) 
    
});
