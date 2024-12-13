function setManifest() {
    const ver = document.getElementById('ver');
    const selectedOption = ver.options[ver.selectedIndex];
    const isBluetoothVersion = document.getElementById('ble').checked;
    const isSPHMicrophone = document.getElementById('sph').checked;
    const selectedVersion = ver.options[ver.selectedIndex].text;
    
    let manifestKey;
    if (selectedVersion === 'WLED.0.15.0') {
        // WLED only needs microphone selection
        manifestKey = 'data-' + (isSPHMicrophone ? 'sph' : 'gma');
    } else {
        // Handle GLORB versions
        let ledmapSuffix;
        if (selectedVersion === 'GLORB.0.14.4-b5' || selectedVersion === 'GLORB.0.14.4-b4') {
            ledmapSuffix = document.getElementById('ledmap83').checked ? '83' : '81';
        } else {
            ledmapSuffix = document.getElementById('ledmap81').checked ? '81' : '80';
        }

        const versionPrefix = isBluetoothVersion ? 'data-ble-' : 'data-plain-';
        const microphoneSuffix = isSPHMicrophone ? 'sph-' : 'gma-';
        manifestKey = versionPrefix + microphoneSuffix + ledmapSuffix;
    }

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
    
    // Show version options only for b1 and b2
    const showVersionOptions = selectedVersion === 'GLORB.0.14.4-b2' || selectedVersion === 'GLORB.0.14.4-b1';
    document.getElementById('version-options').style.display = showVersionOptions ? 'block' : 'none';
    
    // Show ledmap options for GLORB versions except WLED
    const showLedmapOptions = selectedVersion !== 'WLED.0.15.0' && 
        (showVersionOptions || selectedVersion === 'GLORB.0.14.4-b5' || 
         selectedVersion === 'GLORB.0.14.4-b4' || selectedVersion === 'GLORB.0.14.4-b3');
    document.getElementById('ledmap-options').style.display = showLedmapOptions ? 'block' : 'none';

    // Handle ledmap visibility based on version
    const ledmap80 = document.getElementById('ledmap80');
    const ledmap81 = document.getElementById('ledmap81');
    const ledmap83 = document.getElementById('ledmap83');
    const sphOption = document.getElementById('sph');
    const gmaOption = document.getElementById('gma');

    if (selectedVersion === 'WLED.0.15.0') {
        // For WLED, only show microphone options
        document.getElementById('ble').checked = true;
        
        // Show both mic options
        sphOption.style.display = 'inline-block';
        sphOption.nextElementSibling.style.display = 'inline-block';
        gmaOption.style.display = 'inline-block';
        gmaOption.nextElementSibling.style.display = 'inline-block';
    } else if (selectedVersion === 'GLORB.0.14.4-b5') {
        // Existing b5 logic...
        ledmap80.style.display = 'none';
        ledmap80.nextElementSibling.style.display = 'none';
        ledmap81.style.display = 'inline-block';
        ledmap81.nextElementSibling.style.display = 'inline-block';
        ledmap83.style.display = 'inline-block';
        ledmap83.nextElementSibling.style.display = 'inline-block';
        
        sphOption.style.display = 'inline-block';
        sphOption.nextElementSibling.style.display = 'inline-block';
        gmaOption.style.display = 'inline-block';
        gmaOption.nextElementSibling.style.display = 'inline-block';
        
        gmaOption.checked = true;
        ledmap83.checked = true;
    } else if (selectedVersion === 'GLORB.0.14.4-b4') {
        // For b4, show only 83
        ledmap80.style.display = 'none';
        ledmap80.nextElementSibling.style.display = 'none';
        ledmap81.style.display = 'none';
        ledmap81.nextElementSibling.style.display = 'none';
        ledmap83.style.display = 'inline-block';
        ledmap83.nextElementSibling.style.display = 'inline-block';
        
        // Hide SPH option, show only GMA
        sphOption.style.display = 'none';
        sphOption.nextElementSibling.style.display = 'none';
        gmaOption.style.display = 'inline-block';
        gmaOption.nextElementSibling.style.display = 'inline-block';
        
        // Force ledmap83, GMA and BLE for b4
        gmaOption.checked = true;
        document.getElementById('ble').checked = true;
        ledmap83.checked = true;
    } else if (selectedVersion === 'GLORB.0.14.4-b3') {
        // For b3, show only 81
        ledmap80.style.display = 'none';
        ledmap80.nextElementSibling.style.display = 'none';
        ledmap81.style.display = 'inline-block';
        ledmap81.nextElementSibling.style.display = 'inline-block';
        ledmap83.style.display = 'none';
        ledmap83.nextElementSibling.style.display = 'none';
        
        // Show both mic options
        sphOption.style.display = 'inline-block';
        sphOption.nextElementSibling.style.display = 'inline-block';
        gmaOption.style.display = 'inline-block';
        gmaOption.nextElementSibling.style.display = 'inline-block';
        
        // Force ledmap81 and BLE for b3
        document.getElementById('ble').checked = true;
        ledmap81.checked = true;
    } else {
        // For other versions, show only 80 and 81
        ledmap80.style.display = 'inline-block';
        ledmap80.nextElementSibling.style.display = 'inline-block';
        ledmap81.style.display = 'inline-block';
        ledmap81.nextElementSibling.style.display = 'inline-block';
        ledmap83.style.display = 'none';
        ledmap83.nextElementSibling.style.display = 'none';
        
        // Show both mic options
        sphOption.style.display = 'inline-block';
        sphOption.nextElementSibling.style.display = 'inline-block';
        gmaOption.style.display = 'inline-block';
        gmaOption.nextElementSibling.style.display = 'inline-block';
        
        // Reset to SPH and ledmap80 for other versions
        sphOption.checked = true;
        ledmap80.checked = true;
    }

    // Reset to default values when hiding
    if (!showVersionOptions) {
        document.getElementById('ble').checked = true;
    }

    setManifest();
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