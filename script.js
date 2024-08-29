function setManifest() {
    var sel = document.getElementById('ver');
    var opt = sel.options[sel.selectedIndex];
    var m = opt.dataset.manifest;
    var mble = opt.dataset.ble;

    //handle bluetooth checkbox
    m = handleCheckbox(m, mble, 'ble');

    document.getElementById('inst').setAttribute('manifest', m);
    document.getElementById('verstr').textContent = opt.text;
}



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
    document.getElementById('ble').checked = false;
    document.getElementById('ble').disabled = false;
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