import asyncio
from kasa import SmartPlug, Discover


async def discover_devices():
    devices = await Discover.discover()
    plugs, lights = {}, {}
    for device in devices.values():
        await device.update()
        if device.is_strip:
            for child in device.children:
                plugs[child.device_id] = child
        if device.is_plug:
            plugs[device.device_id] = device
        if device.is_bulb:
            lights[device.device_id] = device
    return plugs, lights


async def energy_use():
    plugs, light = await discover_devices()

    while True:
        for device in plugs.values():
            wattage = await device.current_consumption()
            emeter = await device.get_emeter_realtime()
            kwh_monthly = device.emeter_this_month
            #print(f'{device.alias}: {wattage}W ({kwh_monthly} kWh this month)')
            print(f'{device.alias}: {emeter}')
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(energy_use())
