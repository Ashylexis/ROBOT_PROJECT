from pathlib import Path

path = Path(r'c:\Projects\GitProjects\Robot\ROBOT_PROJECT\web_page.py')
text = path.read_text(encoding='utf-8')
marker = 'const missionsData = JSON.parse(""""""'
replacement = r'''const missionsData = JSON.parse("""" + safe_missions_json + """");

function loadMissions() {
    try {
        const parsed = missionsData;
        document.getElementById('missionEditor').value = JSON.stringify(parsed, null, 2);
        document.getElementById('saveStatus').innerText = 'Missionen geladen.';
    } catch (err) {
        document.getElementById('missionEditor').value = JSON.stringify(missionsData, null, 2);
        document.getElementById('saveStatus').innerText = 'Fehler beim Laden der Missionen: ' + err;
    }
}

function saveMissions() {
    const data = document.getElementById('missionEditor').value;
    document.getElementById('saveStatus').innerText = 'Speichere...';
    fetch(baseUrl + '/', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({cmd: 'save_missions', mission_data: data})
    })
    .then(function(response) { return response.text(); })
    .then(function(_) {
        document.getElementById('saveStatus').innerText = 'Missionen gespeichert. Zurück zur Startseite, um die Änderungen zu nutzen.';
    })
    .catch(function(error) {
        document.getElementById('saveStatus').innerText = 'Fehler beim Speichern: ' + error;
    });
}

loadMissions();
</script>

</body>
</html>
'''
if marker not in text:
    raise SystemExit('marker not found')
path.write_text(text.replace(marker, replacement, 1), encoding='utf-8')
print('patched web_page.py')
