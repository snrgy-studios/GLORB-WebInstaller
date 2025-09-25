function setManifest() {
    const ver = document.getElementById('ver');
    const selectedOption = ver.options[ver.selectedIndex];
    const manifest = selectedOption.getAttribute('data-manifest');

    if (manifest) {
        document.getElementById('inst').setAttribute('manifest', manifest);
    } else {
        console.error('Manifest not found for the selected option');
    }
}

function checkSupported() {
    if (document.getElementById('inst').hasAttribute('install-unsupported')) {
        unsupported();
    } else {
        setManifest();
    }
}

function unsupported() {
    document.getElementById('flasher').innerHTML = `Sorry, your browser is not yet supported!<br>
    Please try on Desktop Chrome or Edge.<br>`;
}

// Initialize the page
checkSupported();