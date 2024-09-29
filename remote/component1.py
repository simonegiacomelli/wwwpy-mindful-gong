import wwwpy.remote.component as wpc
import js
from pyodide.ffi import create_proxy

class Component1(wpc.Component, tag_name='component-1'):
    _start_btn: js.HTMLButtonElement = wpc.element()
    _stop_btn: js.HTMLButtonElement = wpc.element()
    totalTime: js.HTMLDivElement = wpc.element()
    countdown: js.HTMLDivElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
        <div>v1.0.7</div>
        <button data-name="_start_btn">Start</button>
        &nbsp;
        <button data-name="_stop_btn">Stop</button>
        <div style="height: 8px; border: none; margin: none;"></div>
        <div data-name="totalTime">#</div>
        <br>
        <div data-name="countdown">#</div>
        """
        js.window.pyodide.setDebug(True)
        self.intervalID = None
        self.cycleTime = 60
        self.wakeLock = None
        self.startTime = None

        self.resetUi()

    def formatTime(self, seconds):
        if seconds is None or seconds < 0:
            seconds = 0
        minutes = seconds // 60
        remainingSeconds = seconds % 60
        return f'{minutes:02d}:{remainingSeconds:02d}'

    def updateUi(self, countDown, totalTime):
        self.countdown.innerHTML = 'Cycle end:<br>' + self.formatTime(countDown)
        self.totalTime.innerHTML = 'Total time:<br>' + self.formatTime(totalTime)

    def resetUi(self):
        self.updateUi(self.cycleTime, 0)

    def playSound(self):
        audio = js.Audio.new('singing-bowl-gong-69238.mp3')
        audio.play()

    def timerTick(self):
        elapsed = int((js.Date.now() - self.startTime) / 1000)
        cycleUsed = elapsed % self.cycleTime
        if cycleUsed == 0:
            self.playSound()
        self.updateUi(self.cycleTime - cycleUsed, elapsed)

    async def startPlaying(self):
        self.startTime = js.Date.now()
        self.timerTick()
        if hasattr(js.navigator, 'wakeLock'):
            self.wakeLock = await js.navigator.wakeLock.request('screen')
        self.intervalID = js.setInterval( create_proxy(self.timerTick), 1000)

    async def stopPlaying(self):
        if self.intervalID is not None:
            js.clearInterval(self.intervalID)
            self.intervalID = None
        self.resetUi()
        if self.wakeLock is not None:
            await self.wakeLock.release()
            self.wakeLock = None

    async def _start_btn__click(self, event):
        js.console.log('handler _start_btn__click event =', event)
        await self.startPlaying()

    async def _stop_btn__click(self, event):
        js.console.log('handler _stop_btn__click event =', event)
        await self.stopPlaying()
