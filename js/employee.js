document.addEventListener("DOMContentLoaded", function () {
    fetchEmployees();

    const employeeForm = document.getElementById("employeeForm");
    employeeForm.addEventListener("submit", function (e) {
        e.preventDefault();
        saveEmployee();
    });
});

let editMode = false;
let editEmployeeId = null;

function fetchEmployees() {
    fetch('http://127.0.0.1:5000/api/employees')
        .then(res => res.json())
        .then(data => {
            const tableBody = document.getElementById("employeeTableBody");
            tableBody.innerHTML = "";
            data.forEach(emp => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td><i class="fas fa-user-circle"></i></td>
                    <td>${emp.id}</td>
                    <td>${emp.name}</td>
                    <td>${emp.email}</td>
                    <td>${emp.phone}</td>
                    <td>${emp.cnic}</td>
                    <td>${emp.emergency_contact}</td>
                    <td>${emp.role}</td>
                    <td>${emp.salary}</td>
                    <td>
                        <button onclick="editEmployee('${emp.id}')"><i class="fas fa-edit"></i></button>
                        <button onclick="deleteEmployee('${emp.id}')"><i class="fas fa-trash"></i></button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        });
}

function openModal() {
    document.getElementById("employeeModal").style.display = "block";
    document.getElementById("modalTitle").innerText = editMode ? "Edit Employee" : "Add Employee";
}

function closeModal() {
    document.getElementById("employeeModal").style.display = "none";
    document.getElementById("employeeForm").reset();
    editMode = false;
    editEmployeeId = null;
}

function saveEmployee() {
    const employee = {
        id: document.getElementById("empId").value.trim(),
        name: document.getElementById("name").value.trim(),
        email: document.getElementById("email").value.trim(),
        phone: document.getElementById("phone").value.trim(),
        cnic: document.getElementById("cnic").value.trim(),
        emergency_contact: document.getElementById("emergency").value.trim(),
        role: document.getElementById("role").value,
        salary: document.getElementById("salary").value.trim()
    };

    const url = editMode
        ? `http://127.0.0.1:5000/api/employees/${editEmployeeId}`
        : "http://127.0.0.1:5000/api/employees";
    const method = editMode ? "PUT" : "POST";

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(employee)
    })
        .then(res => res.json())
        .then(data => {
            closeModal();
            fetchEmployees();
        });
}

function editEmployee(id) {
    fetch('http://127.0.0.1:5000/api/employees')
        .then(res => res.json())
        .then(data => {
            const emp = data.find(e => e.id === id);
            if (emp) {
                editMode = true;
                editEmployeeId = id;
                document.getElementById("empId").value = emp.id;
                document.getElementById("name").value = emp.name;
                document.getElementById("email").value = emp.email;
                document.getElementById("phone").value = emp.phone;
                document.getElementById("cnic").value = emp.cnic;
                document.getElementById("emergency").value = emp.emergency_contact;
                document.getElementById("role").value = emp.role;
                document.getElementById("salary").value = emp.salary;
                openModal();
            }
        });
}

function deleteEmployee(id) {
    if (confirm("Are you sure you want to delete this employee?")) {
        fetch(`http://127.0.0.1:5000/api/employees/${id}`, {
            method: "DELETE"
        })
            .then(res => res.json())
            .then(data => {
                fetchEmployees();
            });
    }
}

window.onclick = function (event) {
    const modal = document.getElementById("employeeModal");
    if (event.target === modal) {
        closeModal();
    }
};
