const form = document.getElementById('student-form');
const analyticsButton = document.getElementById('analytics-button');

form.addEventListener('submit', (e) => {
    e.preventDefault();
    const course = document.getElementById('course').value;
    const gender = document.querySelector('input[name="gender"]:checked').value;
    const location = document.getElementById('location').value;
    const attendance = document.getElementById('attendance').value;

    // Send data to backend using fetch API
    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            course,
            gender,
            location,
            attendance
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    })
    .then(() => {
        window.location.reload()
    })
    .catch(error => console.error('Error:', error));
});

analyticsButton.addEventListener('click', () => {
    window.location.href = '/analytics';
});