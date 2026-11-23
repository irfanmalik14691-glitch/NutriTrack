/**
 * NutriTrack 3D - Cinematic Hero 3D Scene (Three.js)
 */

window.addEventListener('load', () => {
    const container = document.getElementById('three-hero-canvas');
    if (!container) return;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 0, 7.5);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    container.appendChild(renderer.domElement);

    // Group for objects
    const mainGroup = new THREE.Group();
    scene.add(mainGroup);

    // 1. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    const pointGreen = new THREE.PointLight(0x00e676, 3, 20);
    pointGreen.position.set(4, 3, 4);
    scene.add(pointGreen);

    const pointCyan = new THREE.PointLight(0x06b6d4, 2.5, 20);
    pointCyan.position.set(-4, -3, 3);
    scene.add(pointCyan);

    const backLight = new THREE.DirectionalLight(0xffffff, 0.8);
    backLight.position.set(0, 5, -5);
    scene.add(backLight);

    // 2. High-Tech 3D Hexagonal Dumbbell
    const dumbbell = new THREE.Group();

    // Metallic Material
    const ironMaterial = new THREE.MeshStandardMaterial({
        color: 0x18201a,
        metalness: 0.85,
        roughness: 0.25
    });

    // Neon Accent Material
    const neonMaterial = new THREE.MeshStandardMaterial({
        color: 0x00e676,
        emissive: 0x00e676,
        emissiveIntensity: 0.6,
        metalness: 0.5,
        roughness: 0.2
    });

    // Handle (Knurled Bar)
    const handleGeo = new THREE.CylinderGeometry(0.14, 0.14, 3.2, 32);
    const handleMesh = new THREE.Mesh(handleGeo, ironMaterial);
    handleMesh.rotation.z = Math.PI / 2;
    dumbbell.add(handleMesh);

    // Center Grip Ring
    const gripRingGeo = new THREE.TorusGeometry(0.16, 0.03, 16, 32);
    const gripRing = new THREE.Mesh(gripRingGeo, neonMaterial);
    gripRing.rotation.y = Math.PI / 2;
    dumbbell.add(gripRing);

    // Weight Plates Generator (Hexagonal geometry)
    function createHexPlate(radius, thickness, posX) {
        const shape = new THREE.CylinderGeometry(radius, radius, thickness, 6);
        const plate = new THREE.Mesh(shape, ironMaterial);
        plate.rotation.z = Math.PI / 2;
        plate.position.x = posX;

        // Glowing edge bevel
        const bevelGeo = new THREE.TorusGeometry(radius * 0.95, 0.025, 16, 6);
        const bevel = new THREE.Mesh(bevelGeo, neonMaterial);
        bevel.rotation.y = Math.PI / 2;
        bevel.position.x = posX;

        const plateGroup = new THREE.Group();
        plateGroup.add(plate);
        plateGroup.add(bevel);
        return plateGroup;
    }

    // Left Plates
    dumbbell.add(createHexPlate(1.1, 0.35, -1.2));
    dumbbell.add(createHexPlate(0.9, 0.3, -1.6));

    // Right Plates
    dumbbell.add(createHexPlate(1.1, 0.35, 1.2));
    dumbbell.add(createHexPlate(0.9, 0.3, 1.6));

    // Dumbbell tilt
    dumbbell.rotation.x = 0.4;
    dumbbell.rotation.y = 0.6;
    dumbbell.rotation.z = 0.3;
    mainGroup.add(dumbbell);

    // 3. Floating 3D Particles
    const particleCount = 200;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 14;
        positions[i + 1] = (Math.random() - 0.5) * 10;
        positions[i + 2] = (Math.random() - 0.5) * 8;

        // Colors: Green & Cyan blend
        colors[i] = 0.0;
        colors[i + 1] = 0.9;
        colors[i + 2] = Math.random() > 0.5 ? 0.46 : 0.83;
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const particleMat = new THREE.PointsMaterial({
        size: 0.07,
        vertexColors: true,
        transparent: true,
        opacity: 0.7,
        blending: THREE.AdditiveBlending
    });

    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // 4. Mouse Interactive Parallax
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    window.addEventListener('mousemove', (e) => {
        const windowHalfX = window.innerWidth / 2;
        const windowHalfY = window.innerHeight / 2;
        mouseX = (e.clientX - windowHalfX) * 0.0008;
        mouseY = (e.clientY - windowHalfY) * 0.0008;
    });

    // 5. Animation Loop
    let clock = new THREE.Clock();

    function animate() {
        requestAnimationFrame(animate);
        const elapsedTime = clock.getElapsedTime();

        // Dumbbell Floating & Rotation
        dumbbell.rotation.y += 0.006;
        dumbbell.rotation.x += 0.003;
        dumbbell.position.y = Math.sin(elapsedTime * 1.5) * 0.15;

        // Particles gentle drift
        particles.rotation.y = elapsedTime * 0.04;

        // Smooth Mouse Parallax
        targetX += (mouseX - targetX) * 0.05;
        targetY += (mouseY - targetY) * 0.05;
        mainGroup.rotation.y = targetX * 1.5;
        mainGroup.rotation.x = targetY * 1.5;

        renderer.render(scene, camera);
    }
    animate();

    // 6. Responsive Resize
    window.addEventListener('resize', () => {
        if (!container) return;
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
});
