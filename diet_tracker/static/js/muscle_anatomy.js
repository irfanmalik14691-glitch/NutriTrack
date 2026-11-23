/**
 * NutriTrack 3D - Anatomically Accurate Human Muscle Anatomy Explorer
 * Features Independent Left & Right Muscle Meshes, Deltoid Heads, Front/Back Views & Exercise Intel
 */

window.addEventListener('load', () => {
    const container = document.getElementById('anatomy-3d-canvas');
    if (!container) return;

    // 1. Loading Overlay Indicator
    const loadingOverlay = document.createElement('div');
    loadingOverlay.id = 'anatomy-loading-overlay';
    loadingOverlay.style.cssText = `
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(6, 9, 7, 0.94);
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        z-index: 50; transition: opacity 0.6s ease;
    `;
    loadingOverlay.innerHTML = `
        <div style="font-size: 2.4rem; color: #00e676; margin-bottom: 14px;">
            <i class="fa-solid fa-atom fa-spin"></i>
        </div>
        <div style="font-family: var(--font-heading); font-weight: 700; color: #fff; font-size: 1.15rem; letter-spacing: 0.04em;">
            INITIALIZING ANATOMICAL MUSCLE MESHES
        </div>
        <div style="font-size: 0.82rem; color: #94a39b; margin-top: 6px;">
            Separating Left & Right bilateral heads and deltoid divisions...
        </div>
    `;
    container.style.position = 'relative';
    container.appendChild(loadingOverlay);

    // 2. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, container.clientWidth / container.clientHeight, 0.1, 100);
    camera.position.set(0, 0.3, 7.8);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.35;
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    // 3. OrbitControls
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 2.4;
    controls.maxDistance = 12.0;
    controls.maxPolarAngle = Math.PI / 1.75;
    controls.target.set(0, 0, 0);

    // 4. Studio Lighting for Muscle Definition & Contours
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.65);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
    keyLight.position.set(4, 7, 5);
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x06b6d4, 0.55);
    fillLight.position.set(-5, -2, 4);
    scene.add(fillLight);

    // Green Rim Light from behind to contour muscle edges
    const rimLight = new THREE.DirectionalLight(0x00e676, 1.5);
    rimLight.position.set(0, 5, -5.5);
    scene.add(rimLight);

    const floorLight = new THREE.DirectionalLight(0x10b981, 0.35);
    floorLight.position.set(0, -6, 2);
    scene.add(floorLight);

    // 5. Rotating Pedestal Platform
    const pedestalGroup = new THREE.Group();
    const pedestalGeo = new THREE.CylinderGeometry(2.1, 2.3, 0.16, 48);
    const pedestalMat = new THREE.MeshStandardMaterial({
        color: 0x0a120e,
        metalness: 0.9,
        roughness: 0.25
    });
    const pedestal = new THREE.Mesh(pedestalGeo, pedestalMat);
    pedestal.position.y = -3.45;
    pedestalGroup.add(pedestal);

    const ringGeo = new THREE.TorusGeometry(2.12, 0.035, 16, 64);
    const ringMat = new THREE.MeshStandardMaterial({
        color: 0x00e676,
        emissive: 0x00e676,
        emissiveIntensity: 0.9
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.PI / 2;
    ring.position.y = -3.37;
    pedestalGroup.add(ring);
    scene.add(pedestalGroup);

    // 6. Muscle & Tendon Materials
    const realisticMuscleMat = new THREE.MeshStandardMaterial({
        color: 0x852727,       // Natural deep crimson muscle tone
        roughness: 0.45,
        metalness: 0.15,
        emissive: 0x180606,
        emissiveIntensity: 0.18
    });

    const tendonMat = new THREE.MeshStandardMaterial({
        color: 0xd8cebf,       // Pearl ivory tendon/aponeurosis
        roughness: 0.35,
        metalness: 0.12,
        emissive: 0x12100d,
        emissiveIntensity: 0.12
    });

    const hoverMat = new THREE.MeshStandardMaterial({
        color: 0x00e676,
        emissive: 0x00e676,
        emissiveIntensity: 0.65,
        metalness: 0.2,
        roughness: 0.3
    });

    const activeMat = new THREE.MeshStandardMaterial({
        color: 0x00e676,
        emissive: 0x00e676,
        emissiveIntensity: 0.95,
        metalness: 0.1,
        roughness: 0.2
    });

    // 7. Anatomical Muscle Mapping Dictionary
    const MUSCLE_DEFS = {
        'pectoralis-major': { group: 'chest', name: 'Pectoralis Major', isBilateral: true, isBack: false },
        'pectoralis-minor': { group: 'chest', name: 'Pectoralis Minor', isBilateral: true, isBack: false },
        'serratus-anterior': { group: 'chest', name: 'Serratus Anterior', isBilateral: true, isBack: false },
        'subclavius': { group: 'chest', name: 'Subclavius', isBilateral: true, isBack: false },

        // Deltoids (special 3-head split)
        'deltoid': { isDeltoid: true, isBilateral: true },

        'biceps-brachii': { group: 'biceps', name: 'Biceps Brachii', isBilateral: true, isBack: false },
        'brachialis': { group: 'biceps', name: 'Brachialis', isBilateral: true, isBack: false },
        'coracobrachialis': { group: 'biceps', name: 'Coracobrachialis', isBilateral: true, isBack: false },

        'triceps-brachii': { group: 'triceps', name: 'Triceps Brachii', isBilateral: true, isBack: true },
        'anconeus': { group: 'triceps', name: 'Anconeus', isBilateral: true, isBack: true },

        'brachioradialis': { group: 'forearms', name: 'Brachioradialis', isBilateral: true, isBack: false },
        'pronator-teres': { group: 'forearms', name: 'Pronator Teres', isBilateral: true, isBack: false },
        'flexor-carpi-radialis': { group: 'forearms', name: 'Flexor Carpi Radialis', isBilateral: true, isBack: false },
        'flexor-carpi-ulnaris': { group: 'forearms', name: 'Flexor Carpi Ulnaris', isBilateral: true, isBack: false },
        'extensor-carpi-radialis-longus': { group: 'forearms', name: 'Extensor Carpi Radialis', isBilateral: true, isBack: false },
        'extensor-digitorum': { group: 'forearms', name: 'Extensor Digitorum', isBilateral: true, isBack: false },

        'rectus-abdominis': { group: 'abs', name: 'Rectus Abdominis (Six-Pack Core)', isBilateral: false, isBack: false },
        'external-oblique': { group: 'obliques', name: 'External Oblique', isBilateral: true, isBack: false },
        'internal-oblique': { group: 'obliques', name: 'Internal Oblique', isBilateral: true, isBack: false },
        'transversus-abdominis': { group: 'abs', name: 'Transversus Abdominis', isBilateral: false, isBack: false },
        'linea-alba': { group: 'abs', name: 'Linea Alba', isTendon: true, isBilateral: false, isBack: false },

        'latissimus-dorsi': { group: 'lats', name: 'Latissimus Dorsi (Lats)', isBilateral: true, isBack: true },
        'trapezius': { group: 'traps', name: 'Trapezius', isBilateral: false, isBack: true },
        'rhomboid-major': { group: 'traps', name: 'Rhomboid Major', isBilateral: true, isBack: true },
        'rhomboid-minor': { group: 'traps', name: 'Rhomboid Minor', isBilateral: true, isBack: true },
        'levator-scapulae': { group: 'traps', name: 'Levator Scapulae', isBilateral: true, isBack: true },

        'iliocostalis': { group: 'lower-back', name: 'Iliocostalis (Spinal Erectors)', isBilateral: true, isBack: true },
        'longissimus': { group: 'lower-back', name: 'Longissimus (Spinal Erectors)', isBilateral: true, isBack: true },
        'spinalis': { group: 'lower-back', name: 'Spinalis (Spinal Erectors)', isBilateral: true, isBack: true },
        'quadratus-lumborum': { group: 'lower-back', name: 'Quadratus Lumborum', isBilateral: true, isBack: true },
        'multifidus': { group: 'lower-back', name: 'Multifidus', isBilateral: true, isBack: true },

        'gluteus-maximus': { group: 'glutes', name: 'Gluteus Maximus', isBilateral: true, isBack: true },
        'gluteus-medius': { group: 'glutes', name: 'Gluteus Medius', isBilateral: true, isBack: true },
        'gluteus-minimus': { group: 'glutes', name: 'Gluteus Minimus', isBilateral: true, isBack: true },
        'tensor-fasciae-latae': { group: 'glutes', name: 'Tensor Fasciae Latae', isBilateral: true, isBack: false },

        'rectus-femoris': { group: 'quadriceps', name: 'Rectus Femoris (Quad)', isBilateral: true, isBack: false },
        'vastus-lateralis': { group: 'quadriceps', name: 'Vastus Lateralis (Outer Quad)', isBilateral: true, isBack: false },
        'vastus-medialis': { group: 'quadriceps', name: 'Vastus Medialis (Teardrop Quad)', isBilateral: true, isBack: false },
        'vastus-intermedius': { group: 'quadriceps', name: 'Vastus Intermedius', isBilateral: true, isBack: false },
        'sartorius': { group: 'quadriceps', name: 'Sartorius', isBilateral: true, isBack: false },

        'biceps-femoris': { group: 'hamstrings', name: 'Biceps Femoris (Hamstrings)', isBilateral: true, isBack: true },
        'semitendinosus': { group: 'hamstrings', name: 'Semitendinosus (Hamstrings)', isBilateral: true, isBack: true },
        'semimembranosus': { group: 'hamstrings', name: 'Semimembranosus (Hamstrings)', isBilateral: true, isBack: true },

        'gastrocnemius': { group: 'calves', name: 'Gastrocnemius (Calves)', isBilateral: true, isBack: true },
        'soleus': { group: 'calves', name: 'Soleus (Deep Calf)', isBilateral: true, isBack: true },
        'tibialis-anterior': { group: 'calves', name: 'Tibialis Anterior (Shin)', isBilateral: true, isBack: false },
        'calcaneal-tendon': { group: 'calves', name: 'Achilles Tendon', isTendon: true, isBilateral: true, isBack: true }
    };

    const tendonKeywords = ['aponeurosis', 'tendon', 'linea-alba', 'ligament'];

    let allInteractiveMeshes = [];
    let currentActiveMesh = null;
    let hoveredMesh = null;

    // Helper: Split a geometry by an index filter predicate
    function createSubMesh(originalMesh, indices, meta) {
        if (!indices || indices.length === 0) return null;
        const subGeo = originalMesh.geometry.clone();
        subGeo.setIndex(indices);

        const isTendon = meta.isTendon || tendonKeywords.some(t => (meta.name || '').toLowerCase().includes(t));
        const mat = isTendon ? tendonMat.clone() : realisticMuscleMat.clone();

        const mesh = new THREE.Mesh(subGeo, mat);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.userData = {
            ...meta,
            defaultMat: mat
        };
        allInteractiveMeshes.push(mesh);
        return mesh;
    }

    // 8. Load the Realistic 3D Muscular GLB Asset
    const loader = new THREE.GLTFLoader();
    const modelUrl = '/static/models/muscles.glb';

    loader.load(modelUrl, (gltf) => {
        const rootModel = gltf.scene;
        const processedGroup = new THREE.Group();

        // Collect meshes to process
        const meshesToProcess = [];
        rootModel.traverse((child) => {
            if (child.isMesh) meshesToProcess.push(child);
        });

        meshesToProcess.forEach((child) => {
            const rawName = (child.name || child.parent?.name || '').toLowerCase();
            const def = MUSCLE_DEFS[rawName];
            const geo = child.geometry;
            const posAttr = geo.attributes.position;
            const indexAttr = geo.index;

            // SPECIAL CASE: Deltoids (Split into 6 meshes: Front L/R, Side L/R, Rear L/R)
            if (def && def.isDeltoid && posAttr && indexAttr) {
                const indices = indexAttr.array;
                const frontLeft = [], frontRight = [];
                const sideLeft = [], sideRight = [];
                const rearLeft = [], rearRight = [];

                for (let i = 0; i < indices.length; i += 3) {
                    const i1 = indices[i], i2 = indices[i + 1], i3 = indices[i + 2];
                    const x = (posAttr.getX(i1) + posAttr.getX(i2) + posAttr.getX(i3)) / 3.0;
                    const z = (posAttr.getZ(i1) + posAttr.getZ(i2) + posAttr.getZ(i3)) / 3.0;

                    if (z > -0.05) {
                        // Front Deltoid
                        if (x < 0) frontLeft.push(i1, i2, i3);
                        else frontRight.push(i1, i2, i3);
                    } else if (z > -0.20) {
                        // Side Deltoid
                        if (x < 0) sideLeft.push(i1, i2, i3);
                        else sideRight.push(i1, i2, i3);
                    } else {
                        // Rear Deltoid
                        if (x < 0) rearLeft.push(i1, i2, i3);
                        else rearRight.push(i1, i2, i3);
                    }
                }

                const mFL = createSubMesh(child, frontLeft, { groupKey: 'front-deltoids', muscleName: 'Left Front Deltoid', isBack: false });
                const mFR = createSubMesh(child, frontRight, { groupKey: 'front-deltoids', muscleName: 'Right Front Deltoid', isBack: false });
                const mSL = createSubMesh(child, sideLeft, { groupKey: 'side-deltoids', muscleName: 'Left Side Deltoid', isBack: false });
                const mSR = createSubMesh(child, sideRight, { groupKey: 'side-deltoids', muscleName: 'Right Side Deltoid', isBack: false });
                const mRL = createSubMesh(child, rearLeft, { groupKey: 'rear-deltoids', muscleName: 'Left Rear Deltoid', isBack: true });
                const mRR = createSubMesh(child, rearRight, { groupKey: 'rear-deltoids', muscleName: 'Right Rear Deltoid', isBack: true });

                [mFL, mFR, mSL, mSR, mRL, mRR].forEach(m => m && processedGroup.add(m));
                return;
            }

            // BILATERAL SPLIT CASE: (Separate Left and Right meshes)
            if (def && def.isBilateral && posAttr && indexAttr) {
                const indices = indexAttr.array;
                const leftIndices = [];
                const rightIndices = [];

                for (let i = 0; i < indices.length; i += 3) {
                    const i1 = indices[i], i2 = indices[i + 1], i3 = indices[i + 2];
                    const x = (posAttr.getX(i1) + posAttr.getX(i2) + posAttr.getX(i3)) / 3.0;
                    if (x < 0) leftIndices.push(i1, i2, i3);
                    else rightIndices.push(i1, i2, i3);
                }

                if (leftIndices.length > 0 && rightIndices.length > 0) {
                    const mLeft = createSubMesh(child, leftIndices, {
                        groupKey: def.group,
                        muscleName: `Left ${def.name}`,
                        isBack: def.isBack
                    });
                    const mRight = createSubMesh(child, rightIndices, {
                        groupKey: def.group,
                        muscleName: `Right ${def.name}`,
                        isBack: def.isBack
                    });
                    if (mLeft) processedGroup.add(mLeft);
                    if (mRight) processedGroup.add(mRight);
                    return;
                }
            }

            // STANDARD SINGLE MESH (e.g. Abs, Traps, Facial)
            const isTendon = (def && def.isTendon) || tendonKeywords.some(t => rawName.includes(t));
            const baseMat = isTendon ? tendonMat.clone() : realisticMuscleMat.clone();
            child.material = baseMat;
            child.castShadow = true;
            child.receiveShadow = true;

            child.userData = {
                groupKey: def ? def.group : 'other',
                muscleName: def ? def.name : (child.name || 'Muscle'),
                isBack: def ? def.isBack : false,
                defaultMat: baseMat
            };
            allInteractiveMeshes.push(child);
            processedGroup.add(child);
        });

        // Center and position the whole anatomical figure
        const box = new THREE.Box3().setFromObject(processedGroup);
        const center = box.getCenter(new THREE.Vector3());
        processedGroup.position.x = -center.x;
        processedGroup.position.y = -center.y - 0.1;
        processedGroup.position.z = -center.z;

        scene.add(processedGroup);

        // Remove loading overlay smoothly
        loadingOverlay.style.opacity = '0';
        setTimeout(() => loadingOverlay.remove(), 600);

        // Initial selection: Chest
        setTimeout(() => {
            selectMuscleGroup('chest');
        }, 300);

    }, undefined, (error) => {
        console.error('Error loading anatomy GLB model:', error);
        loadingOverlay.innerHTML = `
            <div style="color: #f43f5e; font-size: 1.5rem; margin-bottom: 8px;"><i class="fa-solid fa-triangle-exclamation"></i></div>
            <div style="color: #fff; font-weight: 600;">Failed to load 3D anatomy asset.</div>
            <div style="color: #94a39b; font-size: 0.8rem; margin-top: 4px;">Please refresh or check network connectivity.</div>
        `;
    });

    // 9. Raycasting: Mouse Hover & Click
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    const tooltip = document.getElementById('anatomy-tooltip');

    function onMouseMove(event) {
        if (!allInteractiveMeshes.length) return;

        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(allInteractiveMeshes);

        if (intersects.length > 0) {
            const hitMesh = intersects[0].object;
            container.style.cursor = 'pointer';

            if (hoveredMesh !== hitMesh) {
                // Restore previous hovered mesh if not currently selected
                if (hoveredMesh && hoveredMesh !== currentActiveMesh) {
                    hoveredMesh.material = hoveredMesh.userData.defaultMat;
                }
                hoveredMesh = hitMesh;

                // Apply hover glow only to this specific mesh!
                if (hoveredMesh !== currentActiveMesh) {
                    hoveredMesh.material = hoverMat;
                }
            }

            // Display floating HUD tooltip
            if (tooltip) {
                tooltip.style.display = 'block';
                tooltip.style.left = (event.clientX - rect.left + 16) + 'px';
                tooltip.style.top = (event.clientY - rect.top - 36) + 'px';
                tooltip.innerHTML = `
                    <div style="font-weight:700; color:#fff;">${hitMesh.userData.muscleName}</div>
                    <div style="color:#00e676; font-size:0.75rem; margin-top:2px;">Click to inspect machine & home exercises</div>
                `;
            }
        } else {
            container.style.cursor = 'default';
            if (hoveredMesh && hoveredMesh !== currentActiveMesh) {
                hoveredMesh.material = hoveredMesh.userData.defaultMat;
            }
            hoveredMesh = null;
            if (tooltip) tooltip.style.display = 'none';
        }
    }
    renderer.domElement.addEventListener('mousemove', onMouseMove);

    // Mouse Click Handler
    function onMouseClick(event) {
        if (!allInteractiveMeshes.length) return;

        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(allInteractiveMeshes);

        if (intersects.length > 0) {
            const hitMesh = intersects[0].object;
            selectSingleMuscleMesh(hitMesh);
        }
    }
    renderer.domElement.addEventListener('click', onMouseClick);

    // 10. Select Single Muscle Mesh (Highlighted ONLY in Green)
    function selectSingleMuscleMesh(mesh) {
        // Reset previous active mesh
        if (currentActiveMesh) {
            currentActiveMesh.material = currentActiveMesh.userData.defaultMat;
        }

        currentActiveMesh = mesh;
        currentActiveMesh.material = activeMat; // Glows ONLY this specific muscle!

        // Update specific name badge
        const specificBadge = document.getElementById('selected-muscle-specific-name');
        if (specificBadge) {
            specificBadge.textContent = mesh.userData.muscleName;
        }

        const groupKey = mesh.userData.groupKey || 'chest';

        // Update active UI pills
        document.querySelectorAll('.muscle-select-pill').forEach(pill => {
            if (pill.getAttribute('onclick')?.includes(groupKey)) {
                pill.classList.add('active');
            } else {
                pill.classList.remove('active');
            }
        });

        // Smooth camera focus
        focusCameraOnMuscle(mesh.userData.groupKey, mesh.userData.isBack);

        // Fetch targeted exercises
        loadMuscleDetails(groupKey, mesh.userData.muscleName);
    }

    // 11. Select via Category Pill (Selects representative muscle without glowing whole body)
    window.selectMuscleGroup = function(groupKey) {
        // Find matching meshes for this group
        const groupMeshes = allInteractiveMeshes.filter(m => m.userData.groupKey === groupKey);
        if (!groupMeshes.length) return;

        // Reset previous active mesh
        if (currentActiveMesh) {
            currentActiveMesh.material = currentActiveMesh.userData.defaultMat;
        }

        // Highlight the representative muscle (e.g. Left side)
        const primaryMesh = groupMeshes[0];
        currentActiveMesh = primaryMesh;

        // Light up ONLY the matching group meshes (e.g. Left & Right Pecs), NOT the whole body!
        allInteractiveMeshes.forEach(m => {
            if (m.userData.groupKey === groupKey) {
                m.material = activeMat;
            } else {
                m.material = m.userData.defaultMat;
            }
        });

        // Update badge
        const specificBadge = document.getElementById('selected-muscle-specific-name');
        if (specificBadge) {
            specificBadge.textContent = primaryMesh.userData.muscleName;
        }

        // Update active UI pills
        document.querySelectorAll('.muscle-select-pill').forEach(pill => {
            if (pill.getAttribute('onclick')?.includes(groupKey)) {
                pill.classList.add('active');
            } else {
                pill.classList.remove('active');
            }
        });

        // Focus camera according to front or back anatomy
        const isBack = primaryMesh.userData.isBack;
        focusCameraOnMuscle(groupKey, isBack);

        // Fetch exercise intelligence
        loadMuscleDetails(groupKey, primaryMesh.userData.muscleName);
    };

    function focusCameraOnMuscle(groupKey, isBack) {
        if (!window.gsap) return;

        let targetY = 0;
        let camY = 0.3;
        let camZ = isBack ? -6.2 : 6.2;

        switch (groupKey) {
            case 'chest':
                targetY = 1.0; camY = 1.0; camZ = 5.2; break;
            case 'front-deltoids':
                targetY = 1.35; camY = 1.35; camZ = 5.0; break;
            case 'side-deltoids':
                targetY = 1.3; camY = 1.3; camZ = 5.2; break;
            case 'rear-deltoids':
                targetY = 1.3; camY = 1.3; camZ = -5.2; break; // Facing back
            case 'biceps':
                targetY = 0.8; camY = 0.8; camZ = 5.4; break;
            case 'triceps':
                targetY = 0.85; camY = 0.85; camZ = -5.4; break; // Facing back
            case 'forearms':
                targetY = 0.2; camY = 0.2; camZ = 5.4; break;
            case 'abs':
            case 'obliques':
                targetY = 0.45; camY = 0.45; camZ = 5.0; break;
            case 'lats':
                targetY = 1.05; camY = 1.05; camZ = -5.4; break; // Facing back
            case 'traps':
                targetY = 1.4; camY = 1.4; camZ = -5.2; break; // Facing back
            case 'lower-back':
                targetY = 0.6; camY = 0.6; camZ = -5.2; break; // Facing back
            case 'glutes':
                targetY = -0.3; camY = -0.3; camZ = -5.4; break; // Facing back
            case 'quadriceps':
            case 'quads':
                targetY = -1.1; camY = -1.1; camZ = 5.5; break;
            case 'hamstrings':
                targetY = -1.1; camY = -1.1; camZ = -5.5; break; // Facing back
            case 'calves':
                targetY = -2.1; camY = -2.0; camZ = isBack ? -5.5 : 5.5; break;
            default:
                targetY = 0; camY = 0.3; camZ = 7.5; break;
        }

        gsap.to(controls.target, { y: targetY, duration: 1.0, ease: "power2.out" });
        gsap.to(camera.position, { y: camY, z: camZ, duration: 1.0, ease: "power2.out" });
    }

    function loadMuscleDetails(groupKey, specificTitle = '') {
        const panel = document.getElementById('muscle-detail-panel');
        const emptyState = document.getElementById('muscle-empty-state');
        const muscleTitle = document.getElementById('selected-muscle-title');
        const gymContainer = document.getElementById('gym-exercises-list');
        const homeContainer = document.getElementById('home-exercises-list');

        if (!panel) return;

        emptyState.style.display = 'none';
        panel.style.display = 'block';
        muscleTitle.textContent = groupKey.replace('-', ' ').toUpperCase() + ' ANATOMY';

        gymContainer.innerHTML = '<div class="text-center p-4 text-muted"><i class="fa-solid fa-spinner fa-spin text-neon"></i> Loading targeted exercises...</div>';
        homeContainer.innerHTML = '<div class="text-center p-4 text-muted"><i class="fa-solid fa-spinner fa-spin text-neon"></i> Loading targeted exercises...</div>';

        fetch(`/api/muscle-exercises/${groupKey}`)
            .then(res => res.json())
            .then(data => {
                // Gym Machines & Exercises
                if (data.gym_exercises && data.gym_exercises.length > 0) {
                    gymContainer.innerHTML = data.gym_exercises.map(ex => `
                        <div class="exercise-item-card glass-card mb-3 p-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h4 class="h6 mb-0 text-white font-weight-bold">
                                    <i class="fa-solid fa-dumbbell text-neon mr-2"></i> ${ex.name}
                                </h4>
                                <span class="badge badge-gym">${ex.difficulty}</span>
                            </div>
                            <div class="text-secondary small mb-2">
                                <strong>Machine / Equipment:</strong> <span class="text-emerald">${ex.machine_name || ex.equipment}</span>
                            </div>
                            <p class="small text-muted mb-2">${ex.technique}</p>
                            <div class="prescription-row d-flex gap-3 small mb-2">
                                <span class="tag-pill"><i class="fa-solid fa-layer-group text-neon"></i> ${ex.sets} Sets</span>
                                <span class="tag-pill"><i class="fa-solid fa-repeat text-cyan"></i> ${ex.reps} Reps</span>
                                <span class="tag-pill"><i class="fa-solid fa-stopwatch text-yellow"></i> ${ex.rest}s Rest</span>
                            </div>
                            <div class="accordion-tips small mt-2">
                                <div class="text-muted"><strong class="text-neon">Posture:</strong> ${ex.posture}</div>
                                <div class="text-muted"><strong class="text-red">Avoid:</strong> ${ex.mistakes}</div>
                                <div class="text-muted"><strong class="text-yellow">Safety:</strong> ${ex.safety}</div>
                            </div>
                            <a href="/workout-tracker" class="btn btn-sm btn-secondary-glow mt-3 w-100">
                                <i class="fa-solid fa-plus text-neon mr-1"></i> Log in Workout Tracker
                            </a>
                        </div>
                    `).join('');
                } else {
                    gymContainer.innerHTML = '<div class="p-3 text-muted small">Compound exercises cover this anatomical muscle. See related movements.</div>';
                }

                // Home Exercises
                if (data.home_exercises && data.home_exercises.length > 0) {
                    homeContainer.innerHTML = data.home_exercises.map(ex => `
                        <div class="exercise-item-card glass-card mb-3 p-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h4 class="h6 mb-0 text-white font-weight-bold">
                                    <i class="fa-solid fa-house text-cyan mr-2"></i> ${ex.name}
                                </h4>
                                <span class="badge badge-home">${ex.difficulty}</span>
                            </div>
                            <p class="small text-muted mb-2">${ex.technique}</p>
                            <div class="prescription-row d-flex gap-3 small mb-2">
                                <span class="tag-pill"><i class="fa-solid fa-layer-group text-neon"></i> ${ex.sets} Sets</span>
                                <span class="tag-pill"><i class="fa-solid fa-repeat text-cyan"></i> ${ex.reps} Reps</span>
                                <span class="tag-pill"><i class="fa-solid fa-stopwatch text-yellow"></i> ${ex.rest}s Rest</span>
                            </div>
                            <div class="accordion-tips small mt-2">
                                <div class="text-muted"><strong class="text-neon">Technique:</strong> ${ex.steps}</div>
                                <div class="text-muted"><strong class="text-red">Common Error:</strong> ${ex.mistakes}</div>
                            </div>
                            <a href="/workout-tracker" class="btn btn-sm btn-secondary-glow mt-3 w-100">
                                <i class="fa-solid fa-plus text-neon mr-1"></i> Log in Workout Tracker
                            </a>
                        </div>
                    `).join('');
                } else {
                    homeContainer.innerHTML = '<div class="p-3 text-muted small">Bodyweight exercises for this muscle are covered in the Home Workouts section.</div>';
                }
            })
            .catch(err => {
                gymContainer.innerHTML = '<div class="p-3 text-danger">Error loading exercises. Please try again.</div>';
            });
    }

    // 12. View Toolbar Buttons (Front View, Back View, Reset View)
    const btnFront = document.getElementById('view-front-btn');
    const btnBack = document.getElementById('view-back-btn');
    const btnReset = document.getElementById('view-reset-btn');

    if (btnFront && window.gsap) {
        btnFront.addEventListener('click', () => {
            gsap.to(camera.position, { x: 0, y: 0.3, z: 7.8, duration: 1.0, ease: "power2.out" });
            gsap.to(controls.target, { x: 0, y: 0, z: 0, duration: 1.0, ease: "power2.out" });
        });
    }

    if (btnBack && window.gsap) {
        btnBack.addEventListener('click', () => {
            gsap.to(camera.position, { x: 0, y: 0.3, z: -7.8, duration: 1.0, ease: "power2.out" });
            gsap.to(controls.target, { x: 0, y: 0, z: 0, duration: 1.0, ease: "power2.out" });
        });
    }

    if (btnReset && window.gsap) {
        btnReset.addEventListener('click', () => {
            gsap.to(camera.position, { x: 0, y: 0.3, z: 7.8, duration: 1.0, ease: "power2.out" });
            gsap.to(controls.target, { x: 0, y: 0, z: 0, duration: 1.0, ease: "power2.out" });
            if (currentActiveMesh) {
                allInteractiveMeshes.forEach(m => m.material = m.userData.defaultMat);
                currentActiveMesh = null;
            }
        });
    }

    // 13. 60 FPS Render Loop
    function animate() {
        requestAnimationFrame(animate);
        controls.update();

        // Subtle pedestal ambient rotation
        pedestalGroup.rotation.y += 0.0015;

        renderer.render(scene, camera);
    }
    animate();

    // 14. Responsive Resize
    window.addEventListener('resize', () => {
        if (!container) return;
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
});
