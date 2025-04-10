import mitsuba as mi 
import matplotlib.pyplot as plt
import argparse as par

mi.set_variant('cuda_ad_rgb')

#! Does not support participating media (Don't use)
def render_ptracer(scene, spp=16384):
    integrator = mi.load_dict({
        'type': 'ptracer',
        'samples_per_pass': 64, 
    })
    img = mi.render(scene, spp=spp, integrator=integrator)
    mi.Bitmap(img).write(f'ptracer_media_{spp}.exr')

    plt.imshow(img)
    plt.title(f'particle tracer {spp}')
    plt.axis('off')
    plt.show()

def render(scene, spp=3025, vis=False):
    img = mi.render(scene, spp=spp)

    mi.Bitmap(img).write(f'no_denoise_{spp}.exr')

    if vis:
        plt.imshow(img)
        plt.title(f'no denoise, {spp}')
        plt.axis('off')
        plt.show()

def render_albedo(scene, spp=3025, vis=False):
    integrator = mi.load_dict({
        'type': 'aov',
        'aovs': 'albedo:albedo,normals:sh_normal',
        'integrator': {
            'type': 'volpath',
        }
    })
    sensor = scene.sensors()[0]
    to_sensor = sensor.world_transform().inverse()

    mi.render(scene,spp=spp, integrator=integrator)
    noisy_multichannel = sensor.film().bitmap()

    # Denoise the rendered image
    denoiser = mi.OptixDenoiser(input_size=noisy_multichannel.size(), albedo=True, normals=True, temporal=False)
    denoised = denoiser(noisy_multichannel, albedo_ch="albedo", normals_ch="normals", to_sensor=to_sensor)

    if vis:
        fig, axs = plt.subplots(1, 2, figsize=(12, 4))
        noisy = dict(noisy_multichannel.split())['<root>']
        mi.Bitmap(noisy).write(f'prb_noisy_image_{spp}.exr')
        mi.Bitmap(denoised).write(f'prb_denoised_image_{spp}.exr')
        axs[0].imshow(mi.util.convert_to_bitmap(noisy))     
        axs[0].axis('off'); axs[0].set_title(f'noisy (albedo and normals) {spp}')
        axs[1].imshow(mi.util.convert_to_bitmap(denoised))  
        axs[1].axis('off'); axs[1].set_title('denoised')

        plt.axis('off')
        plt.imshow(mi.util.convert_to_bitmap(denoised))
        plt.savefig(f'denoiser_comparison_{spp}.png')
        plt.show()
def render_basic(scene, spp=3025, vis=False):
    noisy = mi.render(scene, spp=spp)
    

    denoiser = mi.OptixDenoiser(input_size=noisy.shape[:2], albedo=False, normals=False, temporal=False)
    denoised = denoiser(noisy)

    mi.Bitmap(noisy).write(f'noisy_image_{spp}.exr')
    mi.Bitmap(denoised).write(f'denoised_image_{spp}.exr')

    if vis:
        fig, axs = plt.subplots(1, 2, figsize=(12, 4))
        axs[0].imshow(mi.util.convert_to_bitmap(noisy))
        axs[0].axis('off'); axs[0].set_title(f'noisy {spp}')
        axs[1].imshow(mi.util.convert_to_bitmap(denoised))
        axs[1].axis('off'); axs[1].set_title('denoised')
        plt.savefig(f'basic_denoiser_comparison_{spp}.png')

        plt.show()


parser = par.ArgumentParser(description="Control rendering parameters")

parser.add_argument('--samples', '-s', type=int, default=512, help='number of samples per pixel. default = 512')
parser.add_argument('--denoise','-d', choices=['basic', 'extra', 'no'], default='none', help='basic: no albedo information is passed. extra: use albedo and normal information')
parser.add_argument('--file', '-f', type=str, default='scene.xml', help='path to a mitsuba 3 xml file.')
parser.add_argument('--visualize', '-v', action='store_true', help='Show visualizations ')
args = parser.parse_args()
# scene = mi.load_file('/home/cameron/Projects/cmpt469-volumetricRenderer/mitsuba3/resources/data/scenes/cbox/cbox.xml')
print(args.samples)
print(args.denoise)

scene = mi.load_file(args.file)

denoise = args.denoise 
spp = args.samples

vis = args.visualize


if denoise == 'basic':
    print(f'Rendering {args.file} with OptiX denoiser at {spp} samples per pixel.')
    render_basic(scene, spp=spp, vis=vis)
elif denoise == 'extra':
    print(f'Rendering {args.file} with Optix denoiser using albedo and normal information at {spp} samples per pixel.')
    render_albedo(scene, spp=spp, vis=vis)
elif denoise =='none':
    print(f'Rendering {args.file} with no denoiser at {spp} samples per pixel.')
    render(scene, spp=spp, vis=vis)
    

