document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("appointment-form");
    const appointmentsList = document.getElementById("appointments");
  
    form.addEventListener("submit", function(event) {
      event.preventDefault();
  
      const name = document.getElementById("name").value;
      const email = document.getElementById("email").value;
      const date = document.getElementById("date").value;
      const time = document.getElementById("time").value;
  
      const appointment = document.createElement("li");
      appointment.innerHTML = `
        <strong>Name:</strong> ${name} <br>
        <strong>Email:</strong> ${email} <br>
        <strong>Date:</strong> ${date} <br>
        <strong>Time:</strong> ${time}
      `;
  
      appointmentsList.appendChild(appointment);
  
      form.reset();
    });
  });