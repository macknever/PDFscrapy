
########################################
### 2020/02/22 Lawrence
### Dataloader
########################################


########################################
###  tutorial from pytorch
###  https://pytorch.org/tutorials/beginner/data_loading_tutorial.html?highlight=dataloader
########################################



########################################
###import part
########################################

from __future__ import print_function, division
import os
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
from skimage import io, transform
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
from PIL import Image
import torchvision


class Killer_Whale_Dataset(Dataset):
    # this is a class for the Killer whale dataset
    
    #first of all override the __init__() method.
    def __init__(self, data_folder,transform = None):
    	# super() method is to use the method in its parent class
        super().__init__()
        self.folder_list = os.listdir(data_folder)
        self.img_path = os.path.join(data_folder,'img/')
        self.mask_path = os.path.join(data_folder,'mask/')
        self.img_list = sorted(os.listdir(self.img_path))
        self.mask_list = sorted(os.listdir(self.mask_path))
        self.transform = transform

    def __getitem__(self,idx):
        img = Image.open(self.img_path+self.img_list[idx]).convert('RGB')
        mask = Image.open(self.mask_path+self.mask_list[idx])
        mask = transforms.Grayscale(num_output_channels=1)(mask)
        mask = np.array(mask)
        print(len(mask))
        obj_ids = np.unique(mask)
        print(len(obj_ids))
        obj_ids = obj_ids[1:]
        print(len(obj_ids))
        masks = mask == obj_ids[:,None,None]
        print(masks)
        masks = torch.as_tensor(masks, dtype=torch.uint8)

        if self.transform:
            self.img = self.transform(img)
            self.img = nn.AdaptiveAvgPool2d((224,224))(self.img)
            # self.mask = self.transform(masks)
            # self.mask = nn.AdaptiveAvgPool2d((224,224))(self.mask)
        

        sample = {'img':self.img,'mask':masks}

        
            
        
        return sample
    def __len__(self):
    	return len(self.img_list)




def Tensor2Image(t):
    trans = transforms.ToPILImage()
    img = trans(t.squeeze())
    return img



class AE(nn.Module):
    def __init__(self):
        super(AE, self).__init__()
        
        
        self.conv2a = nn.Conv2d(in_channels=3, out_channels=6,kernel_size=3,stride = 1)
        self.convtrans2a = nn.ConvTranspose2d(in_channels=6, out_channels=3,kernel_size=3,stride = 1)

    def encode(self, dictionary):
        x = dictionary['img']
       
        h1 = nn.ReLU()(self.conv2a(x))
        return h1
    
    def decode(self, z):
        # batch_size = z.shape[0]
        h2 = nn.ReLU()(self.convtrans2a(z))
        
        
        
        return {'img': h2}

    def forward(self, dictionary):
        z = self.encode(dictionary)        
        poly_dict = self.decode(z)
        return poly_dict


########################################
###To batch up different size images, 
###We should customerize collate_fn funciton
########################################

def my_collate(batch):
    img =[item['img'] for item in batch]
    
    
    return sample


transform = transforms.Compose([transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.5, 0.5, 0.5],
                                                            std=[0.2, 0.2, 0.2])])   

whale_path = './data1'


# whale_data = Killer_Whale_Dataset(whale_path,transform = transform)
# train_loader = torch.utils.data.DataLoader(whale_data,batch_size = 2,shuffle = True,drop_last = False)


whale_data = Killer_Whale_Dataset(whale_path,transform = transform)
print(whale_data[0]['mask'].size())
# ind_val = list(range(0,6))
# ind_train = list(range(6,len(whale_data)))
# print(len(whale_data))

# val_set = torch.utils.data.Subset(whale_data,ind_val)
# train_set = torch.utils.data.Subset(whale_data,ind_train)


# train_loader = torch.utils.data.DataLoader(whale_data,batch_size = 4,shuffle = True,drop_last = False)
# val_loader = torch.utils.data.DataLoader(val_set,batch_size = 2,shuffle = True,drop_last = False)
# print(len(val_set))
# print(len(train_loader))

# iterator = iter(train_loader)
# batch = next(iterator)

# net_test = AE()
# loss_fn = torch.nn.MSELoss()
# optimizer = optim.Adam(net_test.parameters(), lr=0.001)

# for epoch in range(100):
#     iterator = iter(train_loader)
#     for i in range(len(train_loader)):
#         batch = next(iterator)
#         print(type(batch))
#         preds = net_test(batch)
#         loss = loss_fn(preds['img'], batch['mask'])
#         optimizer.zero_grad()
#         loss.backward()
#         optimizer.step()