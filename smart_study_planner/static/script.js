window.onload = () => {
    const dates = document.querySelectorAll('.sub-date');
    if(dates.length > 0) {
        const today = new Date().toISOString().split('T')[0];
        dates.forEach(el => el.min = today);
    }
};

function addSubject() {
    const container = document.getElementById('subjects-container');
    const row = document.createElement('div');
    row.className = 'subject-row';
    const today = new Date().toISOString().split('T')[0];
    
    row.innerHTML = `
        <div class="input-group">
            <label>Subject Name</label>
            <input type="text" class="sub-name" placeholder="e.g. Physics" required>
        </div>
        <div class="input-group">
            <label>Exam Date</label>
            <input type="date" class="sub-date" min="${today}" required>
        </div>
        <div class="input-group">
            <label>Total Topics</label>
            <input type="number" class="sub-topics" placeholder="e.g. 5" min="1" required>
        </div>
        <button type="button" class="btn-danger" onclick="removeSubject(this)">✖</button>
    `;
    container.appendChild(row);
}

function removeSubject(btn) {
    const rows = document.querySelectorAll('.subject-row');
    if (rows.length > 1) {
        btn.closest('.subject-row').remove();
    } else {
        alert("You must have at least one subject to generate a timetable.");
    }
}

const form = document.getElementById('study-form');
if(form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const studyHours = document.getElementById('study-hours').value;
        const subjects = [];
        const rows = document.querySelectorAll('.subject-row');
        
        let isValid = true;
        
        rows.forEach(row => {
            const name = row.querySelector('.sub-name').value.trim();
            const date = row.querySelector('.sub-date').value;
            const topics = row.querySelector('.sub-topics').value;
            
            if(!name || !date || !topics) {
                isValid = false;
            }
            subjects.push({ name, date, topics });
        });
        
        if(!isValid) {
            alert("Please fill in all subject details.");
            return;
        }
        
        document.getElementById('study-form').classList.add('hidden');
        document.getElementById('loading').classList.remove('hidden');
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ study_hours: studyHours, subjects: subjects })
            });
            
            const data = await response.json();
            
            if (data.error) {
                alert(data.error);
                document.getElementById('study-form').classList.remove('hidden');
                document.getElementById('loading').classList.add('hidden');
                return;
            }
            
            if (data.redirect) {
                window.location.href = data.redirect;
            }
            
        } catch (err) {
            console.error(err);
            alert("An error occurred while connecting to the server.");
            document.getElementById('study-form').classList.remove('hidden');
            document.getElementById('loading').classList.add('hidden');
        }
    });
}
