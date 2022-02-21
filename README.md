
# live_rpyc

This package allows interfacing with the LOM (Live Object Model － [docs here](https://structure-void.com/PythonLiveAPI_documentation/Live10.1.19.xml )) from a separate Python interpreter running outside the Ableton Live process.

It consists in a MIDI Remote Script that accepts [RPyC](https://github.com/tomerfiliba/rpyc) connections, bootstrap client code and some helper functions.

Runs on both Mac and Windows versions of Live 10.

Based on code from https://github.com/bkillenit/AbletonAPI


## Quick start

- Make sure you have Python 2.7 installed. Version should match Live's built-in interpreter, otherwise expect RPyC issues.
- Copy LiveRPyC to Live's MIDI Remote Scripts directory
- Enable LiveRPyC in Live → Preferences → MIDI → Control Surfaces
- Run `client.py` to check everything works


## Example client code

```Python
    from live_rpyc import client
    
    def current_song_time_listener():
        print(song.get_current_beats_song_time())
        
    Live = client.connect()
    live_app = Live.Application.get_application()
    song = live_app.get_document()
    
    print('Connected to Ableton Live {}.{}.{}'.format(live_app.get_major_version(),
        live_app.get_minor_version(), live_app.get_bugfix_version()))
    
    client.bind(song.add_current_song_time_listener, song.remove_current_song_time_listener,
        current_song_time_listener)

    client.start_thread()
    
    try:
        input('Try playing/pausing Live or press Enter to exit\n')
    except:
        pass
    
    client.disconnect()
```
