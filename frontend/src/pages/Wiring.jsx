export default function Wiring() {
  return (
    <div>
      <div className="header">
        <h2>Hardware Wiring</h2>
        <p>Reference connections for the demonstration node. Use current-limiting resistors on LEDs.</p>
      </div>
      <div className="grid grid-2">
        <div className="card">
          <h3>ESP32 → OLED (I2C)</h3>
          <div className="wiring">
            <div>VCC → 3.3V</div>
            <div>GND → GND</div>
            <div>SDA → GPIO 21</div>
            <div>SCL → GPIO 22</div>
          </div>
        </div>
        <div className="card">
          <h3>LEDs</h3>
          <div className="wiring">
            <div>Green LED → GPIO 25 (via ~220Ω)</div>
            <div>Yellow LED → GPIO 26 (via ~220Ω)</div>
            <div>Red LED → GPIO 27 (via ~220Ω)</div>
            <div>LED cathodes → GND</div>
          </div>
        </div>
        <div className="card">
          <h3>Buzzer</h3>
          <div className="wiring">
            <div>Buzzer → GPIO 14</div>
            <div>GND → GND</div>
          </div>
        </div>
        <div className="card">
          <h3>Push Button</h3>
          <div className="wiring">
            <div>Button → GPIO 13</div>
            <div>GND → GND</div>
            <div>Internal pull-up enabled in firmware</div>
          </div>
        </div>
      </div>
    </div>
  );
}
