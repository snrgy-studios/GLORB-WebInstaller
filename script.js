function setManifest() {
    const ver = document.getElementById('ver');
    const selectedOption = ver.options[ver.selectedIndex];
    const isBluetoothVersion = document.getElementById('ble').checked;
    const isSPHMicrophone = document.getElementById('sph').checked;
    const isLedmap81 = document.getElementById('ledmap81').checked;

    const versionPrefix = isBluetoothVersion ? 'data-ble-' : 'data-plain-';
    const microphoneSuffix = isSPHMicrophone ? 'sph-' : 'gma-';
    const ledmapSuffix = isLedmap81 ? '81' : '80';

    const manifestKey = versionPrefix + microphoneSuffix + ledmapSuffix;
    const manifest = selectedOption.getAttribute(manifestKey);

    if (manifest) {
        document.getElementById('inst').setAttribute('manifest', manifest);
        const debugInfo = manifestKey.replace('data-', '');
        document.getElementById('debug-info').textContent = `Selected option: ${debugInfo}`;
    } else {
        console.error('Manifest not found for the selected combination');
        document.getElementById('debug-info').textContent = `Error: Manifest not found for ${manifestKey.replace('data-', '')}`;
    }
}

function toggleAdditionalOptions() {
    const ver = document.getElementById('ver');
    const selectedVersion = ver.options[ver.selectedIndex].text;
    const showAdditionalOptions = selectedVersion === 'GLORB.0.14.4-b1';

    document.getElementById('version-options').style.display = showAdditionalOptions ? 'block' : 'none';
    document.getElementById('ledmap-options').style.display = showAdditionalOptions ? 'block' : 'none';

    // Reset to default values when hiding
    if (!showAdditionalOptions) {
        document.getElementById('ble').checked = true;
        document.getElementById('ledmap81').checked = true;
    }

    setManifest();
}

function resetCheckboxes() {
    document.getElementById('sph').checked = true;
    document.getElementById('gma').checked = false;
    document.getElementById('normal').checked = true;
    document.getElementById('ble').checked = false;
    document.getElementById('ledmap80').checked = true;
    document.getElementById('ledmap81').checked = false;

    ['sph', 'gma', 'normal', 'ble', 'ledmap80', 'ledmap81'].forEach(id => {
        document.querySelector(`label[for="${id}"]`).style.opacity = '1';
        document.querySelector(`label[for="${id}"]`).style.cursor = 'pointer';
    });

    toggleAdditionalOptions();
}

function checkSupported() {
    if (document.getElementById('inst').hasAttribute('install-unsupported')) unsupported();
    else {
        setManifest();
        toggleAdditionalOptions();
    }
}

function unsupported() {
    document.getElementById('flasher').innerHTML = `Sorry, your browser is not yet supported!<br>
    Please try on Desktop Chrome or Edge.<br>`;
}

// Initialize the page
checkSupported();