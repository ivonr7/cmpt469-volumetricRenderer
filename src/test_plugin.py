import mitsuba as mi
from mitsuba.plugins.myphase import MyPhase

mi.set_variant('llvm_ad_rgb')

scene = mi.load_dict({
    "type": "scene",
    "myintegrator": {
        "type": "path",
    },
    "mysensor": {
        "type": "perspective",
        "near_clip": 1.0,
        "far_clip": 1000.0,
        "to_world": mi.ScalarTransform4f().look_at(origin=[1, 1, 1],
                                                 target=[0, 0, 0],
                                                 up=[0, 0, 1]),
        "myfilm": {
            "type": "hdrfilm",
            "rfilter": {
                "type": "box"
            },
            "width": 1024,
            "height": 768,
        }, "mysampler": {
            "type": "independent",
            "sample_count": 4,
        },
    },
    "myemitter": {
        "type": "constant"
    },
    "myshape": {
        "type": "sphere",
        "mybsdf": {
            "type": "diffuse",
            "reflectance": {
                "type": "rgb",
                "value": [0.8, 0.1, 0.1],
            }
        }
    }
})


image = mi.render(scene,spp=256)
mi.util.write_bitmap('test.png',image)
