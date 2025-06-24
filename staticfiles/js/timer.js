function startTimer(elementId, remainingSeconds) {
    const element = document.getElementById(elementId);
    if (!element || remainingSeconds <= 0) {
        if (element) {
            element.innerText = 'Overdue';
            element.classList.remove('bg-info');
            element.classList.add('bg-danger');
        }
        return;
    }

    function updateTimer() {
        if (remainingSeconds <= 0) {
            element.innerText = 'Overdue';
            element.classList.remove('bg-info');
            element.classList.add('bg-danger');
            return;
        }

        const hours = Math.floor(remainingSeconds / 3600);
        const minutes = Math.floor((remainingSeconds % 3600) / 60);
        const seconds = remainingSeconds % 60;

        element.innerText = `${hours}h ${minutes}m ${seconds}s`;
        remainingSeconds -= 1;
    }

    updateTimer();
    setInterval(updateTimer, 1000);
}