import mitsuba as mi
mi.set_variant('llvm_ad_rgb')
from mitsuba import ScalarTransform4f as T

from argparse import ArgumentParser
import os
def create_sensor(sampler:str = 'independent',sc:int = 16,sensor_params:dict = None):
     transform = sensor_params['to_world'].matrix
     return mi.load_dict({
        'type': 'perspective',
        'fov': sensor_params['x_fov'],
        'to_world': None,
        'sampler': {
            'type': sampler,
            'sample_count': sc
        },
        'film': {
            'type': 'hdrfilm',
            'width': sensor_params['film.size'][0],
            'height': sensor_params['film.size'][0],
            'rfilter': {
                'type': 'tent',
            },
            'pixel_format': 'rgb',
        },
    })
def main(mitsuba_xml:str,output_folder:str,
         *,spp:int = 256,depth:int = 8,accel:str = 'cuda_ad_rgb',
         filename:str = None):
     if filename == None: filename = f'render_samples_{spp}_depth_{depth}.png'
     if not os.path.exists(output_folder): os.mkdir(output_folder)
     mi.set_variant(accel)
     scene = mi.load_file(mitsuba_xml)
     integrator = mi.load_dict(
          {
           'type':'volpath',
           "max_depth":depth
          }
     )
     sensor_params = mi.traverse(scene.sensors()[0])
     # Render the scene
     image = mi.render(scene,integrator=integrator, spp=spp)

     # Save the output
     mi.util.write_bitmap(os.path.join(output_folder,filename), image)

if __name__ == "__main__":
     parser = ArgumentParser()
     parser.add_argument("mi_xml",type=str,help="path to mitsuba xml file")
     parser.add_argument("output",type=str,help="folder to write render")
     parser.add_argument("-f",type=str,default=None,help="filename for render")
     parser.add_argument('-s',type=int,default=256,help='samples per pixel')
     parser.add_argument('-d',type=int,default=1,help="depth of volumetric path tracer")
     parser.add_argument('-m',type=str,default='cuda_ad_rgb',help="device to render on (mitsuba)")
     
     
     args = parser.parse_args()
     main(
          args.mi_xml,args.output,
          spp=args.s,depth=args.d,
          accel=args.m,filename=args.f
     )
