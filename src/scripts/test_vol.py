import mitsuba as mi

import sys
if __name__ == "__main__":
    mi.set_variant('cuda_ad_rgb')  # Set the variant
    scene:mi.Scene = mi.load_file(sys.argv[1])
    volume = mi.load_dict({
        "type": "cube",
        "to_world": mi.ScalarTransform4f().scale(100),
        "interior": {
            "type": "homogeneous",
            "sigma_t": {
                "type": "rgb",
                "value": [0.2, 0.2, 0.2]  # Light absorption/scattering
            },
            "albedo": {
                "type": "rgb",
                "value": [0.9, 0.9, 0.9]  # Scattering albedo
            },
            "scale": 1.0,
            "phase": {
                "type": "isotropic"
            }
        }
    })
    scene.shapes().append(volume)
    # Render the scene

    scene_dict = {
    'type': 'scene',
    'integrator': {'type': 'prbvolpath'},
    'object': {
        'type': 'cube',
        'bsdf': {'type': 'null'},
        'interior': {
            "type": "homogeneous",
            "sigma_t": {
                "type": "rgb",
                "value": [0.2, 0.2, 0.2]  # Light absorption/scattering
            },
            "albedo": {
                "type": "rgb",
                "value": [0.9, 0.9, 0.9]  # Scattering albedo
            },
            "scale": 1.0,
            "phase": {
                "type": "isotropic"
            }
        }
    },
    'emitter': {'type': 'constant'}
    }
    image = mi.render(mi.load_dict(scene_dict), spp=64)

    # Save the output
    mi.util.write_bitmap("my_first_render.png", image)
