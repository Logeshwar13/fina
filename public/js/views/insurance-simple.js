// Simple insurance page for testing
export default async function renderInsurance() {
    return `
        <div class="page-header">
            <div>
                <h1 class="page-title">Insurance Management</h1>
                <p class="page-subtitle">Manage your insurance policies and assess coverage needs</p>
            </div>
        </div>

        <div class="card">
            <div class="card-body">
                <h3>Insurance Feature</h3>
                <p>The insurance feature is working! You can:</p>
                <ul>
                    <li>Add and manage insurance policies</li>
                    <li>Run risk assessments</li>
                    <li>Get coverage recommendations</li>
                </ul>
                <button id="test-btn" class="btn btn-primary">Test Button</button>
            </div>
        </div>
    `;
}

// Simple initialization
setTimeout(() => {
    const testBtn = document.getElementById('test-btn');
    if (testBtn) {
        testBtn.addEventListener('click', () => {
            alert('Insurance page is working!');
        });
    }
}, 100);