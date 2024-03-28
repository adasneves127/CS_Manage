(((seconds) => {
    var refresh,
        intvrefresh = () => {
            clearInterval(refresh);
            refresh = setTimeout(() => {
                getTableData()
            }, seconds * 1000);
        };

    $(document).on('keypress click', () => { intvrefresh() });
    intvrefresh();

})(5));

filterData = {}
function reloadTable(){
    applyFilters();
    getTableData();
}




function applyFilters(){
    filterData['status'] = {}
    let statusCheckboxes = document.getElementById("statusFilter").getElementsByTagName("input")
    for(let i = 0; i < statusCheckboxes.length; i++){
        filterData['status'][statusCheckboxes[i].id] = statusCheckboxes[i].checked
    }

    filterData['types'] = {}
    let typeCheckboxes = document.getElementById("typeFilter").getElementsByTagName("input")
    for(let i = 0; i < typeCheckboxes.length; i++){
        filterData['types'][typeCheckboxes[i].id] = typeCheckboxes[i].checked
    }

}



function getTableData(){
    let xhr = new XMLHttpRequest()
    xhr.open("POST", "/finances/table/")
    xhr.setRequestHeader("Content-Type", "application/json")
    // Set the filterData object as the payload
    xhr.send(JSON.stringify(filterData))

    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4){
            if(xhr.status === 200){
                document.getElementById("tableTarget").innerHTML = xhr.responseText
            }
        }
    }
}