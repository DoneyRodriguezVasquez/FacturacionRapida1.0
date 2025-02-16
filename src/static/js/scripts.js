function dragStart(event) {
    event.dataTransfer.setData("Text", event.target.id);
    document.getElementById(event.target.id).classList.add("dragging");
    ide = document.getElementById(event.target.id).getElementsByClassName("properties")[0].getAttribute("value");
    event.dataTransfer.setData("id",ide);
}
function allowDrop(event) {
    event.preventDefault();
}
function drop(event) {
    var status = "";
    if (event.target.id != "") {
        event.preventDefault();
        const data = event.dataTransfer.getData("Text");
        id = event.dataTransfer.getData("id");
        event.target.appendChild(document.getElementById(data));
        // todo list
        if (event.target.id == "TO_DO") {
            document.getElementById(data).classList.remove("border-warning", "border-success", "border-secondary");
            document.getElementById(data).classList.add("border-primary");
            document.getElementById(data).getElementsByClassName("project-name")[0].classList.remove("bg-warning", "bg-success", "bg-secondary");
            document.getElementById(data).getElementsByClassName("project-name")[0].classList.add("bg-primary")
            status = event.target.id;
            update_status(id, status);
        }
        // waiting list
        if (event.target.id == "WAITING") {
            document.getElementById(data).classList.remove("border-primary", "border-success","border-warning",);
            document.getElementById(data).classList.add("border-secondary");
            document.getElementById(data).getElementsByClassName("project-name")[0].classList.remove("bg-primary", "bg-success","bg-warning",);
            document.getElementById(data).getElementsByClassName("project-name")[0].classList.add("bg-secondary")
            status = event.target.id;
            update_status(id, status);
        }
        
        // progress list
        if (event.target.id == "IN_PROGRESS") {
            document.getElementById(data).classList.remove("border-primary", "border-success", "border-secondary");
            document.getElementById(data).classList.add("border-warning");
            document.getElementById(data).getElementsByClassName("project-name")[0].classList.remove("bg-primary", "bg-success","bg-secondary");
            document.getElementById(data).getElementsByClassName("project-name")[0].classList.add("bg-warning");
            status = event.target.id;
            update_status(id, status);
        }

        // completed list
        if (event.target.id == "DONE") {
            document.getElementById(data).classList.remove("border-warning", "border-success", "border-secondary");
            document.getElementById(data).classList.add("border-success");
            document.getElementById(data).getElementsByClassName("project-name")[0].classList.remove("bg-warning", "bg-success","bg-secondary");
            document.getElementById(data).getElementsByClassName("project-name")[0].classList.add("bg-success")
            status = event.target.id;
            update_status(id, status);
        }

        //update task status
        function update_status(id, status){
            $.ajax({
                type: "GET",
                url: '{{ '/' }}',
                data: { id: id, status: status, value:'dragged' },
                success: function callback(response){
                            console.log("success");
                            refreshPage();
                         }
             });
        }
    }
}
function handleStatusChange(event){
    var id = event.target.getAttribute("id");
    var status = event.target.value;
    console.log("id:", id);
    console.log("status:", status);
    $.ajax({
        type: "GET",
        url: '{{ '/' }}',
        data: { id: id, status: status, value:'changed' },
        success: function callback(response){
                    console.log("success");
                }
    });
}
function refreshPage(){
    location.href = location.href;
}

// Función para manejar el cambio en el radio button
function handleRadioButtonChange() {
    var filterType = 'filter_user';
    var filterValue = $('input[name="user_filter"]:checked').val();

    filterTasks(filterType, filterValue);
    $("#user_filters").prop("checked", true);
}

// Función para manejar el cambio en el select de proyectos
function handleProjectSelectChange() {
    var filterType = 'filter_project';
    var filterValue = $('#project_select').val();
    var filterText = $('#project_select option:selected').text();

    filterTasks(filterType, filterValue);
}

// Función para manejar el clic en el botón que restablece los filtros
function resetFilters() {
    // Aquí puedes agregar lógica adicional si es necesario
    // Por ejemplo, podrías llamar a la función filterTasks con valores predeterminados
    filterTasks('', '');
}

// Función para enviar la solicitud al servidor y actualizar la lista de tareas
function filterTasks(filterType, filterValue) {
    $.ajax({
        type: 'GET',
        url: '{{ '/' }}',  
        data: {
            'value': 'filtered',
            'filter_type': filterType,
            'filter_value': filterValue,
        },
        success: function(response) {
            console.log('Success');
            $('#tasks').html(response);
        }
    });
}