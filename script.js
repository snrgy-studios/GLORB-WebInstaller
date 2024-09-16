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
        // Display the selected data option for debugging
        document.getElementById('debug-info').textContent = `Selected option: ${manifestKey}`;
    } else {
        console.error('Manifest not found for the selected combination');
        document.getElementById('debug-info').textContent = `Error: Manifest not found for ${manifestKey}`;
        // You might want to disable the install button or show an error message here
    }
}

// Call setManifest initially to set the correct manifest
setManifest();

function handleCheckbox(manifest, checkboxmanifest, primaryCheckbox) {
    //Check if specified manifest is available

    if (!checkboxmanifest) {
        document.getElementById(primaryCheckbox).disabled = true;
        document.getElementById(primaryCheckbox + "_label").classList.remove("radio__label");
        document.getElementById(primaryCheckbox + "_label").classList.add("disabled__label");
    } else {
        document.getElementById(primaryCheckbox + "_label").classList.remove("disabled__label");
        document.getElementById(primaryCheckbox + "_label").classList.add("radio__label");
    }


    if (checkboxmanifest && document.getElementById(primaryCheckbox).checked) {
        manifest = checkboxmanifest;
    }
    return manifest;
}

function resetCheckboxes() {
    // Reset version
    document.getElementById('normal').checked = true;
    document.getElementById('ble').checked = false;

    // Reset microphone
    document.getElementById('sph').checked = true;
    document.getElementById('gma').checked = false;

    // Reset ledmap
    document.getElementById('ledmap80').checked = true;
    document.getElementById('ledmap81').checked = false;

    // Enable all options
    document.getElementById('ble').disabled = false;
    document.getElementById('gma').disabled = false;
    document.getElementById('ledmap81').disabled = false;

    // Reset labels (in case they were disabled)
    ['normal', 'ble', 'sph', 'gma', 'ledmap80', 'ledmap81'].forEach(id => {
        document.querySelector(`label[for="${id}"]`).style.opacity = '1';
        document.querySelector(`label[for="${id}"]`).style.cursor = 'pointer';
    });

    // Call setManifest to update the manifest based on the reset options
    setManifest();
}

function checkSupported() {
    if (document.getElementById('inst').hasAttribute('install-unsupported')) unsupported();
    else setManifest();
}

function unsupported() {
    document.getElementById('flasher').innerHTML = `Sorry, your browser is not yet supported!<br>
    Please try on Desktop Chrome or Edge.<br>`
}

function showSerialHelp() {
    document.getElementById('coms').innerHTML = `Hit "Install" and select the correct COM port.<br><br>
    Try reconnecting your GLORB :)<br><br>
    `;
}