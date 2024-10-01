# Import all required libraries
'''
   
The updated script is designed to handle errors when downloading posts from Instagram. 
If it encounters a post that returns a 404 or 410 error (which means the post is no longer available),
 it won’t crash or stop the entire process like it did to me in the orginal code. 
 Instead, it will simply print a message saying that the post couldn’t
 be downloaded and move on to the next one. This way, even if some posts are missing, the script can continue 
 downloading the rest, making it much more user-friendly and efficient for anyone trying to save content from a profile.
'''
import instaloader
import getpass
import sys
import os

def get_credentials():
    """
    Prompts the user for their Instagram login credentials.

    Returns:
        tuple: A tuple containing the user's Instagram username and password.
    """
    username = input("Enter your Instagram username: ").strip()
    password = getpass.getpass("Enter your Instagram password: ").strip()
    return username, password

def download_posts(loader, profile):
    """
    Downloads all posts from the given Instagram profile using the specified loader.
    Skips posts that are already downloaded or produce 404/410 errors.
    
    Args:
        loader (instaloader.Instaloader): An instance of the Instaloader class.
        profile (instaloader.Profile): The Instagram profile to download posts from.
    """
    # Create a directory with the same name as the Instagram profile
    os.makedirs(profile.username, exist_ok=True)
    
    # Download all posts from the profile
    for post in profile.get_posts():
        # Create a filename based on the post's date and shortcode
        filename = f"{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}_{post.shortcode}"
        
        # Check if the post has already been downloaded (image or video)
        if os.path.exists(f"{profile.username}/{filename}.jpg") or os.path.exists(f"{profile.username}/{filename}.mp4"):
            print(f"Skipping {filename}, already downloaded.")
            continue  # Skip this post if it's already downloaded
        
        try:
            # Attempt to download the post
            loader.download_post(post, target=profile.username)
        except instaloader.exceptions.InstaloaderException as e:
            # Handle specific instaloader exceptions like 404 Not Found or 410 Gone
            if "404" in str(e) or "410" in str(e):
                print(f"Post {filename} returned a 404/410 error. Skipping...")
            else:
                print(f"An error occurred while downloading post {filename}: {str(e)}")
            continue  # Skip to the next post

def main():
    """
    The main function that orchestrates the entire process of downloading Instagram posts.
    """
    # Create an instance of the Instaloader class
    loader = instaloader.Instaloader()

    # Prompt for the Instagram profile to download from
    target_profile = input("Enter the Instagram username to download posts from: ").strip()

    # Check if the user wants to log in (required for private profiles)
    login_choice = input("Do you need to log in to download posts? (yes/no): ").strip().lower()
    
    if login_choice == 'yes':
        # Get the user's Instagram login credentials
        username, password = get_credentials()
        
        try:
            # Attempt to log in to Instagram
            loader.login(username, password)
            print("Login successful!")
        except instaloader.exceptions.BadCredentialsException:
            print("Error: Invalid Instagram username or password.")
            sys.exit(1)
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            print("Error: Two-factor authentication is required.")
            sys.exit(1)
        except instaloader.exceptions.InvalidArgumentException:
            print("Error: Invalid argument provided.")
            sys.exit(1)
    
    try:
        # Retrieve the Instagram profile using the given username
        profile = instaloader.Profile.from_username(loader.context, target_profile)
        
        # Download all posts from the profile
        download_posts(loader, profile)
        
        print(f"All posts downloaded successfully from the profile: {target_profile}")
        
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: The profile '{target_profile}' does not exist.")
        
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        print(f"Error: The profile '{target_profile}' is private and requires following.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
