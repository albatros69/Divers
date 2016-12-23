# HOWTO create an encrypted LVM volume

## A bit of context...
I've recently bought a brand new laptop. Now I'm left with the old one (Lenovo
X121e) which I choose to recycle to watch films or work on the move.
Unfortunately, I've never setup any data encryption of the disk (my bad)...
While I could have reinstalled it from scratch, I thought it would be quicker
to simply create a new LV and move the sensible data onto it (essentially /home).

I've been proved wrong, as I didn't find a tutorial to explain how to do this.
I found documentation to encrypt a whole VG, or other which I didn't manage to
apply successfully... So I combined a few of them and decided to write my own.
Hope this helps!

## The environment
I will suppose you have a working LVM setup, with an existing VG name
`vg_name`. On Debian, it's usually named against the hostname if it has been
created by the installer. We also need some free space for the new LV. Let's
create a new `crypt_lv` LV:

    $ lvcreate -L 10G -n crypt_lv vg_name

You obviously have to adjust the size (and likely the different names, `crypt_lv`
e.g.). Once created, we will erase everything on the new volume for good measure:

    $ badblocks -c 10240 -s -w -t random -v /dev/vg_name/crypt_lv

## Where the encryption starts...
Now we have to setup the encryption on the new volume. The passphrase here is used to protect the cypher key. You will be able to change it later if needed.

    $ cryptsetup luksFormat --cipher aes-xts-plain64 --key-size 256 --hash sha256 /dev/vg_name/crypt_lv
    WARNING!
    ========
    This will overwrite data on /dev/mapper/VolGroup00-myvolume irrevocably.
    
    Are you sure? (Type uppercase yes): YES
    Enter LUKS passphrase:
    Verify passphrase:
    Command successful.
    $

We can now format the encrypted container. I adopt here the Debian convention
for the LVM device mapping, i.e. a concatenation of the VG name and the LV
name. You can do differently as you fancy it:

    $ cryptsetup luksOpen /dev/mapper/vg_name-crypt_lv crypt_vol
    Enter LUKS passphrase for /dev/mapper/vg_name-crypt_lv:
    key slot 0 unlocked.
    Command successful.
    $ mkfs -t ext4 /dev/mapper/crypt_vol

## Mounting the new volume at boot time
To mount the encrypted volume at boot time, you will need to create (or add to)
the `/etc/crypttab` file the following:

    crypt_vol  /dev/mapper/vg_name-crypt_lv   none    luks

And to add the following to `/etc/fstab`:

    /dev/mapper/crypt_vol /mnt/crypt_mnt    ext4    discard,defaults    0   2

Then, reboot. You should be asked at some point the passphrase to unlock the
key. The boot process should then proceed as usual after and you should see
your newly created volume and container. To check everything is OK, you can
issue the following commands:

    $ blkid
    [...]
    /dev/mapper/vg_name-crypt_lv: UUID="<random_stuff>" TYPE="crypto_LUKS"
    /dev/mapper/crypt_vol: UUID="<random_stuff>" TYPE="ext4"
    $ lsblk
    NAME                          MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINT
    [...]
    └─sda3                          ?:?    0 nnn,nG  0 part
    [...]
      └─vg_name-crypt_lv            ?:?    0    10G  0 lvm
        └─crypt_vol                 ?:?    0    10G  0 crypt /mnt/crypt_mnt
    $


## Optional: Securing the data
You can now mount your encrypted volume and copy the data onto it.
    $ mkdir /mnt/crypt_mnt
    $ mount /dev/mapper/crypt_vol /mnt/crypt_mnt
    $ cp -a <your_data> /mnt/crypt_mnt

Once done, you can also erase your old data, either with `shred` or alike, or
more brutally with `dd` or `badblocks`(see above) on the whole volume where
your data reside (**WARNING** You might lose some data if you don't proceed
carefully).

