
# live_rpyc

This package allows interfacing with the LOM (Live Object Model) from a separate Python interpreter running outside the Ableton Live process.

It consists in a MIDI Remote Script that accepts RPyC connections, bootstrap client code and some helper functions.

It has been thoroughly tuned and tested to work on both Mac and Windows versions of Live.


## Quick start

- Make sure you have Python 2.7 installed. Version should match Live's built-in interpreter, otherwise expect RPyC issues.
- Copy LiveRPyC to Live's MIDI Remote Scripts directory
- Enable LiveRPyC in Live → Preferences → MIDI → Control Surfaces
- Run `client.py` to check everything works


## Example client code

    from live_rpyc import client
    
    
    """same as calling api from midi remote script"""
    Live = client.connect()
    live_app = Live.Application.get_application()
    song = live_app.get_document()
    
    print('Connected to Ableton Live {}.{}.{}'.format(live_app.get_major_version(),
        live_app.get_minor_version(), live_app.get_bugfix_version()))
    
    """avoid direct add_*_listener calls and use supplied bind function instead,
       because remove_*_listener calls will fail"""
    client.bind(song.add_current_song_time_listener, song.remove_current_song_time_listener,
        current_song_time_listener)
    
    """do not forget"""
    client.start_thread()
    
    try:
        input('Try playing/pausing Live or press Enter to exit\n')
    except:
        pass
    
    client.disconnect()
