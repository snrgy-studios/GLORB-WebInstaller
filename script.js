function setManifest() {
    const ver = document.getElementById('ver');
    const selectedVersion = ver.options[ver.selectedIndex].text;
    const selectedOption = ver.options[ver.selectedIndex];
    const isSPHMicrophone = document.getElementById('sph').checked;
    
    let manifestKey;
    if (selectedVersion === 'WLED_0.15.0') {
        manifestKey = `data-${isSPHMicrophone ? 'sph' : 'gma'}`;
    } else {
        const microphoneSuffix = isSPHMicrophone ? 'sph' : 'gma';
        const ledmapSuffix = document.getElementById('ledmap83').checked ? '83' : '81';
        manifestKey = `data-${microphoneSuffix}-${ledmapSuffix}`;
    }

    const manifest = selectedOption.getAttribute(manifestKey);

    if (manifest) {
        document.getElementById('inst').setAttribute('manifest', manifest);
    } else {
        console.error('Manifest not found for the selected combination');
    }
}

function toggleOptions() {
    const ver = document.getElementById('ver');
    const selectedVersion = ver.options[ver.selectedIndex].text;
    const ledmapRow = document.getElementById('ledmap-row');

    // Show/hide ledmap options based on version
    ledmapRow.style.display = selectedVersion.startsWith('WLED') ? 'none' : 'block';

    // Reset to default options when changing firmware
    document.getElementById('gma').checked = true;
    document.getElementById('ledmap83').checked = true;

    setManifest();
}

function checkSupported() {
    if (document.getElementById('inst').hasAttribute('install-unsupported')) {
        unsupported();
    } else {
        toggleOptions();
    }
}

function unsupported() {
    document.getElementById('flasher').innerHTML = `Sorry, your browser is not yet supported!<br>
    Please try on Desktop Chrome or Edge.<br>`;
}

// Initialize the page
checkSupported();