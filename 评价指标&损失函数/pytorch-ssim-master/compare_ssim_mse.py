from PIL import Image
import matplotlib.pyplot as plt
import torch
import torch.nn.functional as F
from torchvision import transforms
from torch import optim
from pytorch_ssim import ssim
import imageio
import os

tf = transforms.ToTensor()

img1 = tf(Image.open('test.png').convert("L")).cuda().unsqueeze(0)
img2 = torch.rand(img1.size()).cuda().requires_grad_()
img3 = torch.rand(img1.size()).cuda().requires_grad_()

optimizer_mse = optim.Adam([img2], lr=1e-3)
optimizer_ssim = optim.Adam([img3], lr=1e-3)

step = 0

plt.ion()

fig, axes = plt.subplots(1, 3, figsize=(9, 3))
if not os.path.exists('results'):
    os.mkdir('results')

while True:
    optimizer_mse.zero_grad()
    optimizer_ssim.zero_grad()
    loss_mse = F.mse_loss(img2, img1)
    loss_ssim = -ssim(img3, img1)
    loss_mse.backward()
    loss_ssim.backward()
    optimizer_mse.step()
    optimizer_ssim.step()
    step += 1
    if step % 20 == 0:
        print('Step: {}'.format(step))

        I_origin = img1.detach().cpu().squeeze().numpy()
        I_mse = img2.detach().cpu().squeeze().numpy()
        I_ssim = img3.detach().cpu().squeeze().numpy()

        axes[0].imshow(I_origin, 'gray')
        axes[0].title.set_text('Origin')
        axes[0].axis('off')

        axes[1].imshow(I_mse, 'gray')
        axes[1].title.set_text('MSE loss: {:.3f}'.format(loss_mse.item()))
        axes[1].axis('off')

        axes[2].imshow(I_ssim, 'gray')
        axes[2].title.set_text('SSIM: {:.3f}'.format(-loss_ssim.item()))
        axes[2].axis('off')

        plt.pause(0.1)
        plt.savefig('results/{}.png'.format(step//20))

    if loss_mse.item() < 0.001 and -loss_ssim > 0.999:
        break

plt.ioff()
plt.show()


names = os.listdir('results')
imgs = []

for i in range(len(names)):
    imgs.append(imageio.imread('results/{}.png'.format(i + 1)))

imageio.mimsave('gif.gif', imgs, duration=0.2)
print('GIF generated')
