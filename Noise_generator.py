from .Architecture import icons

from PIL import Image
import math
import copy
import random
import comfy
import math
import torch
import numpy as np

def MON_conv_pil_tensor(img):
	return (torch.from_numpy(np.array(img).astype(np.float32) / 255.0).unsqueeze(0),)

def remap(val, min_val, max_val, min_map, max_map):
	return (val-min_val)/(max_val-min_val) * (max_map-min_map) + min_map

class MON_PlasmaNoise:
   @classmethod
   def INPUT_TYPES(s):
      return {
			"required": {
				"width": ("INT", {
					"default": 512,
					"min": 128,
					"max": 8192,
					"step": 8
				}),
				"height": ("INT", {
					"default": 512,
					"min": 128,
					"max": 8192,
					"step": 8
				}),

				"turbulence": ("FLOAT", {
					"default": 2.75,
					"min": 0.5,
					"max": 32,
					"step": 0.01,
               "display": "slider"
				}),
				
				"value_min": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),
				"value_max": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),

				"red_min": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),
				"red_max": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),
				"green_min": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),
				"green_max": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),
				"blue_min": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),
				"blue_max": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),
				# Does nothing because ComfyUI doesn't understand "static" output nodes
				"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
			}
		}

   RETURN_TYPES = ("IMAGE",)
   FUNCTION = "MON_generate_plasma"
   CATEGORY = icons.get("MyNodes/Noise")


   def MON_generate_plasma(self, width, height, turbulence, value_min, value_max, red_min, red_max, green_min, green_max, blue_min, blue_max, seed):
		# Image size
      w = width
      h = height
      aw = copy.deepcopy(w)
      ah = copy.deepcopy(h)

      outimage = Image.new("RGB", (aw, ah))
      if w >= h:
         h = w
      else:
         w = h

		# Clamp per channel and globally
      clamp_v_min = value_min
      clamp_v_max = value_max
      clamp_r_min = red_min
      clamp_r_max = red_max
      clamp_g_min = green_min
      clamp_g_max = green_max
      clamp_b_min = blue_min
      clamp_b_max = blue_max

      roughness = turbulence
      pixmap = []

      random.seed(seed)
      def adjust(xa, ya, x, y, xb, yb):
         if(pixmap[x][y] == 0):
            d=math.fabs(xa-xb) + math.fabs(ya-yb)
            v=(pixmap[xa][ya] + pixmap[xb][yb])/2.0 + (random.random()-0.555) * d * roughness
            c=int(math.fabs(v + random.randint(-48, 48)))
            if c < 0:
               c = 0
            elif c > 255:
               c = 255
            pixmap[x][y] = c

      def subdivide(x1, y1, x2, y2):
         if(not((x2-x1 < 2.0) and (y2-y1 < 2.0))):
            x=int((x1 + x2)/2.0)
            y=int((y1 + y2)/2.0)
            adjust(x1,y1,x,y1,x2,y1)
            adjust(x2,y1,x2,y,x2,y2)
            adjust(x1,y2,x,y2,x2,y2)
            adjust(x1,y1,x1,y,x1,y2)
            if(pixmap[x][y] == 0):
               v=int((pixmap[x1][y1] + pixmap[x2][y1] + pixmap[x2][y2] + pixmap[x1][y2]) / 4.0)
               pixmap[x][y] = v

            subdivide(x1,y1,x,y)
            subdivide(x,y1,x2,y)
            subdivide(x,y,x2,y2)
            subdivide(x1,y,x,y2)
      pbar = comfy.utils.ProgressBar(4)
      step = 0

      pixmap = [[0 for i in range(h)] for j in range(w)]
      pixmap[0][0] = random.randint(0, 255)
      pixmap[w-1][0] = random.randint(0, 255)
      pixmap[w-1][h-1] = random.randint(0, 255)
      pixmap[0][h-1] = random.randint(0, 255)
      subdivide(0,0,w-1,h-1)
      r = copy.deepcopy(pixmap)

      step += 1
      pbar.update_absolute(step, 4)

      pixmap = [[0 for i in range(h)] for j in range(w)]
      pixmap[0][0] = random.randint(0, 255)
      pixmap[w-1][0] = random.randint(0, 255)
      pixmap[w-1][h-1] = random.randint(0, 255)
      pixmap[0][h-1] = random.randint(0, 255)
      subdivide(0,0,w-1,h-1)
      g = copy.deepcopy(pixmap)

      step += 1
      pbar.update_absolute(step, 4)

      pixmap = [[0 for i in range(h)] for j in range(w)]
      pixmap[0][0] = random.randint(0, 255)
      pixmap[w-1][0] = random.randint(0, 255)
      pixmap[w-1][h-1] = random.randint(0, 255)
      pixmap[0][h-1] = random.randint(0, 255)
      subdivide(0,0,w-1,h-1)
      b = copy.deepcopy(pixmap)

      step += 1
      pbar.update_absolute(step, 4)

      # Handle value clamps
      lv = 0
      mv = 0
      if clamp_v_min == -1:
         lv = 0
      else:
         lv = clamp_v_min

      if clamp_v_max == -1:
         mv = 255
      else:
         mv = clamp_v_max

      lr = 0
      mr = 0
      if clamp_r_min == -1:
         lr = lv
      else:
         lr = clamp_r_min

      if clamp_r_max == -1:
         mr = mv
      else:
         mr = clamp_r_max

      lg = 0
      mg = 0
      if clamp_g_min == -1:
         lg = lv
      else:
         lg = clamp_g_min

      if clamp_g_max == -1:
         mg = mv
      else:
         mg = clamp_g_max

      lb = 0
      mb = 0
      if clamp_b_min == -1:
         lb = lv
      else:
         lb = clamp_b_min

      if clamp_b_max == -1:
         mb = mv
      else:
         mb = clamp_b_max

		#print(f"V:{lv}/{mv}, R:{lr}/{mr}, G:{lg}/{mg}, B:{lb}/{mb}")
      for y in range(ah):
         for x in range(aw):
            nr = int(remap(r[x][y], 0, 255, lr, mr))
            ng = int(remap(g[x][y], 0, 255, lg, mg))
            nb = int(remap(b[x][y], 0, 255, lb, mb))
            outimage.putpixel((x,y), (nr, ng, nb))

      step += 1
      pbar.update_absolute(step, 4)
      return MON_conv_pil_tensor(outimage)
   
class MON_Random_Noise:
	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"width": ("INT", {
					"default": 512,
					"min": 128,
					"max": 8192,
					"step": 8
				}),
				"height": ("INT", {
					"default": 512,
					"min": 128,
					"max": 8192,
					"step": 8
				}),

				"value_min": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),
				"value_max": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),

				"red_min": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),
				"red_max": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),
				"green_min": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),
				"green_max": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),
				"blue_min": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),
				"blue_max": ("INT", {
					"default": -1,
					"min": -1,
					"max": 255,
					"step": 1
				}),
				# Does nothing because ComfyUI doesn't understand "static" output nodes
				"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
			}
		}

	RETURN_TYPES = ("IMAGE",)
	FUNCTION = "MON_generate_noise"
	CATEGORY = icons.get("MyNodes/Noise")

	def MON_generate_noise(self, width, height, value_min, value_max, red_min, red_max, green_min, green_max, blue_min, blue_max, seed):
		# Image size
		w = width
		h = height
		aw = copy.deepcopy(w)
		ah = copy.deepcopy(h)

		outimage = Image.new("RGB", (aw, ah))
		random.seed(seed)

		# Clamp per channel and globally
		clamp_v_min = value_min
		clamp_v_max = value_max
		clamp_r_min = red_min
		clamp_r_max = red_max
		clamp_g_min = green_min
		clamp_g_max = green_max
		clamp_b_min = blue_min
		clamp_b_max = blue_max

		# Handle value clamps
		lv = 0
		mv = 0
		if clamp_v_min == -1:
			lv = 0
		else:
			lv = clamp_v_min

		if clamp_v_max == -1:
			mv = 255
		else:
			mv = clamp_v_max

		lr = 0
		mr = 0
		if clamp_r_min == -1:
			lr = lv
		else:
			lr = clamp_r_min

		if clamp_r_max == -1:
			mr = mv
		else:
			mr = clamp_r_max

		lg = 0
		mg = 0
		if clamp_g_min == -1:
			lg = lv
		else:
			lg = clamp_g_min

		if clamp_g_max == -1:
			mg = mv
		else:
			mg = clamp_g_max

		lb = 0
		mb = 0
		if clamp_b_min == -1:
			lb = lv
		else:
			lb = clamp_b_min

		if clamp_b_max == -1:
			mb = mv
		else:
			mb = clamp_b_max

		pbar = comfy.utils.ProgressBar(ah)
		step = 0
		for y in range(ah):
			for x in range(aw):
				nr = random.randint(lr, mr)
				ng = random.randint(lg, mg)
				nb = random.randint(lb, mb)
				outimage.putpixel((x,y), (nr, ng, nb))
			step += 1
			pbar.update_absolute(step, ah)

		return MON_conv_pil_tensor(outimage)