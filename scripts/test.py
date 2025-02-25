import mitsuba as mi

mi.set_variant('cuda_ad_rgb')  # Set the variant

scene = mi.load_file("monkey.xml")
# Render the scene
image = mi.render(scene, spp=256)

# Save the output
mi.util.write_bitmap("my_first_render.png", image)
