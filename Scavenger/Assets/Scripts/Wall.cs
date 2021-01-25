using UnityEngine;
using System.Collections;

public class Wall : MonoBehaviour
{
    public AudioClip chopSound1;                //1 of 2 audio clips that play when the wall is attacked by the player.
    public AudioClip chopSound2;                //2 of 2 audio clips that play when the wall is attacked by the player.
    public Sprite dmgSprite;                    //Alternate sprite to display after Wall has been attacked by player.
    public int hp = 3;                            //hit points for the wall.

    private SpriteRenderer spriteRenderer;        //Store a component reference to the attached SpriteRenderer.


    void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
    }


    //DamageWall is called when the player attacks a wall.
    public void DamageWall(int loss)
    {
        //SoundManager.instance.RandomizeSfx(chopSound1, chopSound2);

        //Set spriteRenderer to the damaged wall sprite.
        spriteRenderer.sprite = dmgSprite;

        hp -= loss;

        if (hp <= 0)
            gameObject.SetActive(false);
    }
}